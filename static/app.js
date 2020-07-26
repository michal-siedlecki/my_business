var productsFormId = "pf";

function getGross(nett, tax){
  var tax_value = parseFloat(nett)*parseFloat(tax)/100;
  var gross_value = parseFloat(nett)+tax_value;
  return Number((gross_value).toFixed(2));
};

function getNett(gross, tax){
  var dividor = (parseFloat(tax)+100)/100;
  var nett_value = parseFloat(gross)/dividor;
  return Number((nett_value).toFixed(2));
};

function getSum(quantity, value){
  var itemQuantity = parseInt(quantity);
  var itemValue = parseFloat(value);
  return Number((itemValue*itemQuantity).toFixed(2));
}

function getTaxSum(sumValue, tax){
  return Number((sumValue*parseFloat(tax)/100).toFixed(2))
};

function updateNetts(){
  var forms = document.getElementById("product-forms").children;
  for(var i = 0; i<forms.length; i++){
    var form = forms[i];
    var nett = form.children[2].lastChild;
    var tax = form.children[3].lastChild;
    var gross = form.children[4].lastChild;
    nett.value = getNett(gross.value, tax.value);
  };
  updateTotalNettGrossTax();
};

function updateGrosses(){
  var forms = document.getElementById("product-forms").children;
  for(var i = 0; i<forms.length; i++){
    var form = forms[i];
    var nett = form.children[2].lastChild;
    var tax = form.children[3].lastChild;
    var gross = form.children[4].lastChild;
    var quantity = form.children[5].lastChild;
    var nettSum = form.children[6].lastChild;
    var taxSum = form.children[7].lastChild;
    var grossSum = form.children[8].lastChild;
    if (nett.value == "") {
      nett.value = getNett(gross.value, tax.value);

    } else {
      gross.value = getGross(nett.value, tax.value);
      grossSum.value = getSum(quantity.value, gross.value);

    };
    nettSum.value = getSum(quantity.value, nett.value);
    taxSum.value = getTaxSum(nettSum.value, tax.value);

  };
  updateTotalNettGrossTax();
};

function updateTotalNett(){
  var totalNett = document.getElementById("id_total_nett");
  var nettInputs = document.getElementsByName("prod_total_nett");
  var sum = 0.00;
  nettInputs.forEach((input) => {sum += parseFloat(input.value);})
  totalNett.value = Number(sum.toFixed(2));
};

function updateTotalTax(){
  var totalTax = document.getElementById("id_total_tax");
  var taxInputs = document.getElementsByName("prod_total_tax");
  var sum = 0.00;
  taxInputs.forEach((input) => {sum += parseFloat(input.value);})
  totalTax.value = Number(sum.toFixed(2));
};

function updateTotalGross(){
  var totalGrossBold = document.getElementById("totalGrossBold");
  var totalGross = document.getElementById("id_total_gross");
  var grossInputs = document.getElementsByName("prod_total_gross");
  var sum = 0.00;
  grossInputs.forEach((input) => {sum += parseFloat(input.value);})
  totalGross.value = Number(sum.toFixed(2));

  totalGrossBold.innerHTML = `Razem do zapłaty: ${Number(sum.toFixed(2))} zł` ;
};

function updateTotalNettGrossTax(){
  updateTotalNett();
  updateTotalGross();
  updateTotalTax();
};

function addProduct(product_id, name, price_nett, tax_rate, price_gross, quantity = 1){
    var product = {
      product_id : product_id,
      name : name,
      price_nett : price_nett,
      price_gross : price_gross,
      tax_rate : tax_rate,
      quantity : quantity
    };
    if (isLastFormTaken()) {
      addProductForm();
      fillInForm(getLastFormId(), product);
    } else {
      fillInForm(getLastFormId(), product);
    };
};

function getLastFormId(){
  var forms = document.getElementById("product-forms").children;
  return forms[forms.length - 1].id;
};

function isLastFormTaken(){
  var lastFormInputs = document.getElementById(getLastFormId()).getElementsByTagName("input");
  return lastFormInputs[0].value != ""
};

function fillInForm(form_id, product){
  var inputs = document.getElementById(form_id).getElementsByTagName("input");
  for (let [name, value] of Object.entries(product)) {
    for (let input of inputs){
      if (input.name == "price_nett"){
        var input_nett = input;
      }
      if (input.name == name){
        input.value = value;
      };
    };
  };
  input_nett.value = product.price_nett; // rewrite nett price to avoid incorrect values after product.entries iteration
  updateNetts();
  updateGrosses();
  updateTotalNettGrossTax();
};

function addProductForm(){
  var form = document.getElementById("product-forms");
  var productNum = form.children.length;
  var cln = form.children[0].cloneNode(true);
  cln.id = productsFormId + productNum;
  document.getElementById("product-forms").appendChild(cln);
  var newForm = document.getElementById(cln.id);
  for (var i=0; i<newForm.children.length; i++){
    var input = newForm.children[i].lastChild;
    input.value= 0;
  };
  appendRemoveButton(newForm);
  return newForm.id;
};

function appendRemoveButton(element){
  var div = document.createElement("DIV");
  var btn = document.createElement("INPUT");
  btn.type = "button";
  btn.value = "remove";
  btn.setAttribute("onClick", "removeElement('"+element.id+"');");
  div.setAttribute("class", "form-group col-md-1 mb-0");
  div.appendChild(btn);
  element.appendChild(div);
};

function removeElement(elementID){
  var element = document.getElementById(elementID);
  element.remove();
  updateTotalNettGrossTax();
};
