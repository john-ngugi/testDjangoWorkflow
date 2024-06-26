
// Select the form and button elements
const form = document.getElementById('send-layer-info');
const submitButton = document.getElementById('get-layer-btn');
const mapDiv = document.querySelector(".map");
const loadingScreen = document.getElementById('loader');
const layerSelector = document.getElementById('layerSelect');
const attributeSelector = document.getElementById('AttributeSelect');
// Get selected values from the form
const layerSelect = document.getElementById('layerSelect').value;
const attributeSelect = document.getElementById('AttributeSelect').value;


loadingScreen.style.display = 'none';

// Add an event listener to the form submit event
form.addEventListener('submit', function(event) {
    // Get selected values from the form
    const layerSelectFn = document.getElementById('layerSelect').value;
    const attributeSelectFn = document.getElementById('AttributeSelect').value;
        event.preventDefault(); // Prevent the default form submission

        loadingScreen.style.display = 'flex';
        // Construct the data object to be sent
        const data = {
            layerSelect: layerSelectFn,
            attributeSelect: attributeSelectFn
        };

        // Make a POST request using Fetch API
        fetch('get-layer/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // Include CSRF token
            },
            body: JSON.stringify(data) // Convert data to JSON string
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json(); // Parse JSON response
        })
        .then(data => {
            console.log('Success:', data);
            // Handle success response here if needed
            mapDiv.innerHTML = data.map
        })
        .catch(error => {
            console.error('Error:', error);
            // Handle error here
        })
        .catch(error => {
            // Handle error here
        })
        .finally(() => {
            // Hide the loading screen
            loadingScreen.style.display = 'none'
        });
});

// Function to get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Extract CSRF token from cookie
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showQueryLayer() {
    document.getElementById('small-info').style.display = 'none';
    document.getElementById('query-layer').classList.remove('visually-hidden');
}

function hideQueryLayer() {
    document.getElementById('small-info').classList.remove('visually-hidden')
    document.getElementById('query-layer').classList.add('visually-hidden');
}



const maps = document.querySelectorAll(".layer-identifier")
const layerTitle = document.getElementById("layer-title");
const layerInfo = document.getElementById('layer-info');

const layers_dict = {
    'schoolaccessindexwalk': 'school index walk',
    'schoolaccessindexdrive': 'school index drive',
    'schoolaccessratiodrive': 'school access ratio drive',
    'schoolaccessratiowalk': 'school access ratio walk',
    'nbijobsacces_index': 'job access index',
    'nbijobsacces_ratio': 'job access ratio',
    'nbilanduseentropy_areahex': 'land use entropy area',
    'nbilanduseentropy_fn': 'land use entropy function',
    'nbihealthaccess_index': 'Nairobi Health Access Index',
    'nbihealthaccess_ratio': 'Nairobi Health Access Ratio',
    'sdna_1500meters_2018': 'Spatial design network analysis 1.5Km',
    'sdna_1000meters_2018': 'Spatial Design Network Analysis 1km',
    'sdna_500meters_2018': 'Spatial Design Network Analysis 500m'
}

const accesibility_layers = {
    'schoolaccessindexwalk': 'school index walk',
    'schoolaccessindexdrive': 'school index drive',
    'schoolaccessratiodrive': 'school access ratio drive',
    'schoolaccessratiowalk': 'school access ratio walk',
    'nbijobsacces_index': 'job access index',
    'nbijobsacces_ratio': 'job access ratio',
    'nbihealthaccess_index': 'Nairobi Health Access Index',
    'nbihealthaccess_ratio': 'Nairobi Health Access Ratio',
}


const landUse_layers = {
    'nbilanduseentropy_areahex': 'land use entropy area',
    'nbilanduseentropy_fn': 'land use entropy function',
}


const design_layers = {
    'sdna_1500meters_2018': 'Spatial design network analysis 1.5Km',
    'sdna_1000meters_2018': 'Spatial Design Network Analysis 1km',
    'sdna_500meters_2018': 'Spatial Design Network Analysis 500m'

}

const designAttrs = ['shape_leng']
const accessAttrs = ["schoolacce", 'saccinddrv', 'schaccessb','saccindwlk','jobaccindx','jobacratio','accessindx','acessratio']
const entropyAttrs = ['areahex','entropy_fn']


const layerObjs = {
    'Destination Accessibility': accesibility_layers,
    'Design of Road Network': design_layers,
    'Diversity': landUse_layers,
}

const attrsObj = {
    'Destination Accessibility':accessAttrs,
    'Design of Road Network': designAttrs,
    'Diversity':entropyAttrs,
}

function clearChildrenFromIndex(element, startIndex) {
    const children = element.children;
    const length = children.length;
    console.log("length: ",length)
    // Remove children starting from the startIndex
    for (let i = startIndex; i < length; i++) {
            element.removeChild(children[startIndex]);
        }
    }


function getAttrbutes(layer_title){
    clearChildrenFromIndex(attributeSelector,1)
    for(const [key, value] of Object.entries(attrsObj)){
        if(layer_title.innerText == key){
            value.forEach((attr)=>{
                var newElement = `<option value=${attr} title="${attr}">${attr}</option>`
                attributeSelector.insertAdjacentHTML('beforeend', newElement)
            });
        };
    };
}

function getLayernames(layerTitle){
    clearChildrenFromIndex(layerSelector,1)
    for(const [key_outer, value_outer] of Object.entries(layerObjs)){
        if(layerTitle.innerText == key_outer){
            console.log("in loop")
            for (const [key, value] of Object.entries(value_outer)) {
                var newElement = `<option value=${key} title="${value}">${value}</option>`
                layerSelector.insertAdjacentHTML( 'beforeend', newElement );
            };
        };
    };
}


maps.forEach((map)=>{
    console.log(map)
    map.addEventListener('click',()=>  {
        var name = map.text
        console.log("name" , name)
        layerTitle.innerText = name
        getLayernames(layerTitle)
        getAttrbutes(layerTitle)
    });
    clearChildrenFromIndex(layerSelector,1)
});








// const commentsBox = document.getElementById('comments');
// const boxOpener = document.getElementById('box-opener');
// const closeFormBtn = document.getElementById("close-comment-btn")

// boxOpener.addEventListener('click', ()=> {
//         commentsBox.style.display = Flex;
//     })

// closeFormBtn.addEventListener('click',()=>{
//     commentsBox.style.display = 'None'
// })

 /*

  Facility hospital access index
  select between hosital and school (simplified)
  add in a changing opacity*
  add in the overlay for neighbourhoods
  separate the reseach papers
  list of papers
  datasets our datsets
  open linksto open data
  scrapped data inder datasets
  Themes {accessibility opportunity , network analiys properties, zoning }

   sdna = [ mad(clossness centarlity)  diva(sevierance/ separation) len(density) halr(efficiency) tpbta(2 faced-betweenness centrality) ] 1500 = 1.5 killomitres

   density , design(sdna),  opportunity , diversity(entropy), acceccibitlity, distance to public transport , population density
   short description of the layers i.e dates of aquiry for the hospitals ,
   send a layer with shops, mpesa but for now use the ones from OSM


   have a menu where people choose what the person is satisfied and uncertisfied with.
   so that people in the medical or whatever field to have better services.

   have a closed ended and open ended approach to facilities(level of satisfaction)

   feedback- contact page


 */
