import test from 'node:test';
import assert from 'node:assert/strict';
import {computeScenario,validateInputs} from './calculator.mjs';
const base={N:20,O:20,P:5,S:20,R:30};
for(const [O,subscriptionA,subscriptionB,rent,contributionA,contributionB] of [[20,400,400,600,200,200],[16,400,320,480,80,160],[0,400,0,0,-400,0]]){
  test(`proposal check: ${O} occupied apartments`,()=>{
    const r=computeScenario({...base,O}).results;
    assert.deepEqual(r,{rentalIncome:rent,continue:{billable:20,subscription:subscriptionA,contribution:contributionA},pause:{billable:O,subscription:subscriptionB,contribution:contributionB}});
    assert.deepEqual(computeScenario({...base,O,P:4}).results,r,'charger count must not change finances');
  });
}
test('blank monetary assumptions remain missing, including whitespace',()=>{
  for(const raw of [{...base,S:''},{...base,R:''},{...base,S:' '},{...base,S:null},{...base,S:undefined}]){
    const s=computeScenario(raw);assert.equal(s.results,null);assert.equal(s.hasMoney,false);
  }
  assert.equal(computeScenario({...base,S:0,R:0}).results.continue.contribution,0);
});
test('reject invalid counts and bounds without silently rewriting',()=>{
  for(const [key,value] of [['N',0],['N',1.2],['N',''],['O',-1],['O',21],['P',0],['P',21],['P',1.5]]){
    const state=computeScenario({...base,[key]:value});assert.equal(state.results,null);assert.ok(state.errors[key]);
  }
  const state=validateInputs({...base,N:10});assert.equal(state.values.O,20);assert.ok(state.errors.O);
});
test('reject negative, nonfinite and unrepresentable amounts',()=>{
  for(const [key,value] of [['S',-1],['R',-1],['S',Infinity],['R','invalid'],['S',1e300]])assert.equal(computeScenario({...base,[key]:value}).results,null);
});
test('decimal CHF assumptions and negative contributions stay visible',()=>{
  const r=computeScenario({...base,O:16,S:20.5,R:0}).results;
  assert.equal(r.continue.subscription,410);assert.equal(r.pause.subscription,328);assert.equal(r.continue.contribution,-410);
});
