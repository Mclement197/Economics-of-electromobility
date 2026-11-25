import {mountFinance} from './finance-ui.mjs';
const preset=new URLSearchParams(location.search).get('preset')==='cham'?'cham':'zurich';
const planners=[...document.querySelectorAll('[data-finance]')].map(root=>({root,api:mountFinance(root,{preset})}));
function updatePresentationLinks(){
  for(const {root,api} of planners){
    for(const link of root.closest('section').querySelectorAll('[data-finance-present]')){
      link.href=`/praesentation/?live=1&preset=${encodeURIComponent(api.getState().preset)}`;
    }
  }
}
window.addEventListener('voltoshare:finance-change',updatePresentationLinks);
updatePresentationLinks();
