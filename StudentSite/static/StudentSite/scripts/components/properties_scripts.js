var propertiesBlock;
var propertiesOptionalOrderBlock;
var propertiesIsNotDemo = true;

function propertiesInitiateScripts(name) {
    propertiesBlock = document.getElementById(name);
    propertiesOptionalOrderBlock = document.getElementById("optional_order_properties")
}

function propertiesPrepareForDemo() {
    propertiesIsNotDemo = false;
}

function propertiesOrderChanged(isOfOrder) {
    if (isOfOrder) {
        propertiesOptionalOrderBlock.style.display = '';
    } else {
        propertiesOptionalOrderBlock.style.display = 'none';
    }
}

function propertiesChangeVisibility(setVisible) {
    propertiesBlock.style.visibility = (setVisible ? '' : 'collapse')
}

function propertiesSetValue(valueString) {
    console.log("setting" + valueString);
    //valueString содержит имя свойтсва и значение. Пример: reflexivity=reflexive
    //Необходимо установить соответсвтующее значение у блока с этим свойством.
    var inputs =  propertiesBlock.getElementsByTagName("input");
    valueString=valueString.split("=");
    if (valueString[0] == 'order') {
        propertiesOrderChanged(valueString[1] == "of-order");
    }
    for (var i = 0;i<inputs.length;++i)
    {
        if (inputs[i].name==valueString[0]&&inputs[i].value==valueString[1])
        {
            inputs[i].checked=true;
            break;
        }
    }
}

function propertiesUnsetValue(valueString) {
    console.log("unsetting" + valueString);
    valueString=valueString.split("=");
    var inputs = propertiesBlock.getElementsByTagName("input");
    if (valueString[0] == "order") {
        propertiesOrderChanged(false);
    }
    for (var i = 0;i < inputs.length;++i)
    {
        if (valueString[0]==inputs[i].name) {
            inputs[i].checked = false;
        }
    }
}

function propertiesHighlightErrors(correctSolve) {
    console.log("correct:" + correctSolve);

}

function propertiesFromAnswersString(partialSolve) {
    // поступает строка вида
    // reflexivity=non-reflexive anti-reflexivity=anti-reflexive symmetry=non-symmetric asymmetry=asymmetric antisymmetry=antisymmetric transitivity=transitive equivalency=non-equivalent order=of-order order-strict=strict order-linearity=partial
    // на основании этой строки заполнить все свойства

    console.log("partial:" + partialSolve);
}

function propertiesToAnswersString() {
    // Составить строку вида, как в предыдущей функции, на основе заполненных элементов со свойствами.
}