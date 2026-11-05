const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { Readable } = require('node:stream');
const { contextText } = require('../api/enquiry-context');
const handler = require('../api/enquiry');
const valid = { name: 'QA Person', email: 'qa@example.invalid', session_type: 'Recording', message: 'Project', form_started_at: Date.now() - 6000 };
const attribution = {utm_source:'s'.repeat(160), utm_medium:'m'.repeat(160), utm_campaign:'c'.repeat(160), utm_term:'t'.repeat(160), utm_content:'o'.repeat(160),gclid:'g'.repeat(200),gbraid:'b'.repeat(200),wbraid:'w'.repeat(200),landing_page:'/'+'l'.repeat(299)};
const context = {context_version:2, preferred_room:'r'.repeat(160),engineering_support:'e'.repeat(160),duration:'d'.repeat(160),attribution, attribution_consent:{analytics:true,advertising:true}};
async function submit(payload) {
  const req = Readable.from([Buffer.from(JSON.stringify(payload))]);
  req.method = 'POST';req.headers = {origin:'https://www.salvationstudios.co.uk'};
  return new Promise(resolve => handler(req,{setHeader(){},end(body){resolve({status:this.statusCode,...JSON.parse(body)})}}));
}
async function mockedDelivery(run) {
  const keys = ['RESEND_API_KEY','ENQUIRY_FROM_EMAIL','ENQUIRY_SHEETS_WEBHOOK_URL','ENQUIRY_SHEETS_SECRET'];
  const previous = keys.map(k=>process.env[k]);const original = global.fetch;const requests=[];
  Object.assign(process.env,{RESEND_API_KEY:'test-only',ENQUIRY_FROM_EMAIL:'qa@example.invalid',ENQUIRY_SHEETS_WEBHOOK_URL:'https://script.google.com/macros/s/test/exec',ENQUIRY_SHEETS_SECRET:'test-only'});
  global.fetch = async (url,options)=>{requests.push({url,body:JSON.parse(options.body)});return {ok:true,json:async()=>({ok:true})}};
  try { await run(requests); } finally { global.fetch=original; keys.forEach((key,i)=>previous[i]===undefined?delete process.env[key]:process.env[key]=previous[i]); }
}

test('full-size message and context survive in email and Sheet payload without changing the schema', async()=>{
 await mockedDelivery(async requests=>{
  const message = '🎵'.repeat(2000);
  const response = await submit({...valid,...context,message});assert.equal(response.status,200);
  assert.equal(requests.length,2);
  const email=requests[0].body, sheet=requests[1].body.enquiry;
  assert.ok(email.text.includes(message));assert.ok(email.html.includes(message));assert.ok(sheet.message.startsWith(message));
  for(const value of Object.values(attribution)) assert.ok(sheet.message.includes(value));
  for(const key of ['preferred_room','engineering_support','duration'])assert.ok(sheet.message.includes(context[key]));
  assert.ok(sheet.message.length>4000&&sheet.message.length<8000);
  assert.equal(sheet.attribution,undefined);
 });
});

test('legacy payloads do not duplicate context already embedded by the old client',async()=>{
 await mockedDelivery(async requests=>{
  const message='Project\n\nPreferred room: Main studio';
  const response=await submit({...valid,message,preferred_room:'Main studio'});assert.equal(response.status,200);
  assert.equal(requests[1].body.enquiry.message,message);
 });
});

test('limits reject oversized values instead of silently truncating identities or project text',async()=>{
 await mockedDelivery(async requests=>{
  for(const [field,max] of Object.entries({name:120,email:180,artist_company:160,phone:80,dates:180,message:4000,preferred_room:160})){
   const response=await submit({...valid,[field]:'x'.repeat(max+1)});assert.equal(response.status,400);assert.match(response.error,/shorten/);
  }
  assert.equal(requests.length,0);
 });
});

test('invalid object payloads and missing project text cannot be replaced by metadata',async()=>{
 await mockedDelivery(async requests=>{
  for(const payload of [null,[],{...valid,...context,message:''}])assert.equal((await submit(payload)).status,400);
  assert.equal(requests.length,0);
 });
});

test('context validates consent categories, allowed keys and unsafe attribution content',()=>{
 assert.equal(contextText({...context,attribution_consent:{analytics:false,advertising:false}}).includes('Campaign'),false);
 const analytics=contextText({...context,attribution_consent:{analytics:true,advertising:false}});assert.match(analytics,/utm_source/);assert.equal(analytics.includes('gclid:'),false);
 const advertising=contextText({...context,attribution_consent:{analytics:false,advertising:true}});assert.match(advertising,/gclid:/);assert.equal(advertising.includes('utm_source:'),false);
 const unsafe=contextText({attribution:{utm_source:'person@example.com',utm_campaign:'bad\nvalue',gclid:'bad click',email:'do-not-share@example.com'},attribution_consent:{analytics:true,advertising:true}});assert.equal(unsafe,'');
 assert.equal(contextText({attribution:{utm_source:'google'},attribution_consent:{analytics:'true'}}),'');
 assert.match(contextText({preferred_room:'<test>\nroom'}),/^Preferred room: <test> room$/);
});

test('updated Apps Script writes complete 8k context while retaining formula defense and same-ID deduplication',()=>{
 let row;const sheet={getLastRow:()=>1,appendRow:r=>row=r};
 const sandbox={PropertiesService:{getScriptProperties:()=>({getProperty:()=> 'test'})},LockService:{getScriptLock:()=>({waitLock(){},releaseLock(){}})},SpreadsheetApp:{openById:()=>({getSheetByName:()=>sheet})},ContentService:{createTextOutput:text=>({setMimeType:()=>JSON.parse(text)}),MimeType:{JSON:'json'}},console};
 vm.createContext(sandbox);vm.runInContext(fs.readFileSync('integrations/google-sheets-enquiry-webhook/Code.gs','utf8'),sandbox);
 const message='='.repeat(6500);
 const result=sandbox.doPost({postData:{contents:JSON.stringify({secret:'test',enquiry:{...valid,message,submission_id:'abc'}})}});
 assert.equal(result.ok,true);assert.equal(row[7],"'"+message);assert.equal(row.length,12);
 row=null;sheet.getLastRow=()=>2;sheet.getRange=()=>({createTextFinder:()=>({matchEntireCell:()=>({findNext:()=>true})})});
 assert.equal(sandbox.doPost({postData:{contents:JSON.stringify({secret:'test',enquiry:{...valid,submission_id:'abc'}})}}).duplicate,true);assert.equal(row,null);
});
