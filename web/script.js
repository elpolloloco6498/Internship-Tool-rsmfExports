let queryId = 0
let queriesList = []

// Table logic
const queryTable = document.querySelector(".query-table")

// Form logic
const btnAddQuery = document.querySelector(".btn-add-query")
const btnCreateQuery = document.querySelector(".create-btn")
const queryForm = document.querySelector(".query-form")

eel.expose(renderDownloadedDocuments);
function renderDownloadedDocuments(doclist) {
    console.log(doclist)
    htmlContent = ""
    for (let doc of doclist) {
        htmlContent += `
        <div class="doc">
            <div class="date">
                <span class="date-info">${doc["date"]}</span>
            </div>
            <div class="doc-info">
                <h3>
                    <span class="doc-title">${doc["name"]}</span>
                </h3>
            </div>
        </div>
        `
    }
    console.log(htmlContent)
    document.querySelector(".download-area").innerHTML = htmlContent
}

eel.expose(removeDownloadSpinner);
function removeDownloadSpinner() {
    document.querySelector(".spinner-download").innerHTML = `<svg style="width: 1em;height: 1em;" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check" viewBox="0 0 16 16">
		  <path d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.267.267 0 0 1 .02-.022z"></path>
		</svg>`
}

function renderQueryTable(queriesList) {
    queryForm.style.display = "none"
    btnCreateQuery.style.display = "none"

    // empty table
    queryTable.innerHTML = ""

    let i = 0
    for (let query of queriesList) {
        let rowData = document.createElement("tr")
        rowData.innerHTML = `
        <th scope="row">${i}</th>
        <td>${query["name"]}</td>
        <td>${query["searchBy"]}</td>
        <td>${query["searchIds"]}</td>
        <td>${query["exports"]}</td>
        <td><a data-rowid=${i} class="btn-delete-query ui-btn-danger">Delete</a></td>`

        queryTable.appendChild(rowData)

        // delete button logic
        let btnsDeleteQuery = document.querySelectorAll(".btn-delete-query")
        let btn = btnsDeleteQuery[btnsDeleteQuery.length-1]

        i += 1

        btn.addEventListener("click", () => {
            let btnIndex = btn.getAttribute("data-rowid")
            queriesList.splice(btnIndex,1)
            renderQueryTable(queriesList)
        })
    }
}

function getDataForm() {
    // get data from form
    // get query name

    let query = {}

    let selQuery = document.querySelector(".select-query")
    query["name"] = selQuery.options[selQuery.value].text
    // get searchby
    let selSearchBy = document.querySelector(".select-searchBy")
    query["searchBy"] = selSearchBy.options[selSearchBy.value].text

    // get search ids
    let labelIds = []
    let searchIds = document.querySelector(".querySearchIds").value.split(',')
    console.log(searchIds)
    for (let label of searchIds) {
        labelIds.push(label)
    }
    query["searchIds"] = labelIds

    // get exports fields
    let exports = []
    let checkboxs = document.querySelectorAll(".checkboxs-exports div input")
    for (let check of checkboxs) {
        if (check.checked) {
            exports.push(check.nextElementSibling.innerText)
        }
    }
    query["exports"] = exports

    return query
}

let configUi = 'ui.json';
fetch(configUi).then(response => response.json()).then(json => {
uiConf = json

// Display screens name
nameQueries = Object.keys(uiConf["screens"])
htmlContentQueryList = "<option>Select One …</option>"
i = 1
for (let nameQuery of nameQueries) {
    htmlContentQueryList += `<option value=${i}>${nameQuery}</option>`
    i += 1
}
document.querySelector(".select-query").innerHTML = htmlContentQueryList

// Display Export fields relative to selected query
let queryDropDown = document.querySelector(".queries")
document.querySelector(".queries select").addEventListener("change", (e)=>{
    selectedQuery = e.target.options[e.target.value].text
    htmlContentCheckboxs = ""
    for (let field of uiConf["screens"][selectedQuery]["export-fields"]) {
        console.log(field)
        htmlContentCheckboxs += `<div class="form-check form-check-inline">
        <input class="form-check-input" type="checkbox" value="" id="flexCheckDefault">
        <label class="form-check-label" for="flexCheckDefault">
            ${field}
        </label>
    </div>`
    }
    document.querySelector(".checkboxs-content").innerHTML = htmlContentCheckboxs
})

btnAddQuery.addEventListener("click", () => {
    displayStyle = "block"
    if (queryForm.style.display == "block") {
        displayStyle = "none"
        btnAddQuery.innerHTML = "+"
    }
    else {
        displayStyle = "block"
        btnAddQuery.innerHTML = "-"
    }
    queryForm.style.display = displayStyle
    btnCreateQuery.style.display = displayStyle
})
btnCreateQuery.addEventListener("click", () => {
    let query = getDataForm()
    queriesList.push(query)
    renderQueryTable(queriesList)
    queryId += 1
})

// generate json queries
queriesData = {}

const btnExecQueries = document.querySelector(".btn-execute-query")
btnExecQueries.addEventListener("click", ()=>{
    queriesData["queries"] = queriesList

    configJson = JSON.stringify(queriesData, null, 4)
    //console.log(configJson)
    eel.exportDocuments(configJson)
    document.querySelector(".spinner-download").innerHTML = "<div class='spinner-border text-primary'></div>"
})

// end JSON load
});