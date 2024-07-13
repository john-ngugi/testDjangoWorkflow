
// Select the form and button elements
const form = document.getElementById('send-layer-info');
const submitButton = document.getElementById('get-layer-btn');
const mapDiv = document.querySelector(".map");
const loadingScreen = document.getElementById('loader');
const layerSelector = document.getElementById('layerSelect');
const attributeSelector = document.getElementById('AttributeSelect');
const countySelector = document.getElementById('countySelect');
const closeQuery = document.querySelector('.close-query');
const expanationText = document.querySelector(".explanation-text");
const smallTextContent = document.querySelector(".small-info-content");
const commentBoxTitle = document.querySelector(".title-name");
loadingScreen.style.display = 'none';


const countiesOfKenya = [
    'Baringo', 'Bomet', 'Bungoma', 'Busia', 'Elgeyo-Marakwet', 'Embu', 'Garissa', 'Homa Bay', 'Isiolo', 'Kajiado',
    'Kakamega', 'Kericho', 'Kiambu', 'Kilifi', 'Kirinyaga', 'Kisii', 'Kisumu', 'Kitui', 'Kwale', 'Laikipia', 'Lamu',
    'Machakos', 'Makueni', 'Mandera', 'Marsabit', 'Meru', 'Migori', 'Mombasa', 'Murang\'a', 'Nairobi', 'Nakuru', 'Nandi',
    'Narok', 'Nyamira', 'Nyandarua', 'Nyeri', 'Samburu', 'Siaya', 'Taita-Taveta', 'Tana River', 'Tharaka-Nithi',
    'Trans Nzoia', 'Turkana', 'Uasin Gishu', 'Vihiga', 'Wajir', 'West Pokot'
];

const attributeObj = {
    'School accessibility': 'School access index ',
    'Healthcare Accessibility ':'Healthcare Access Index',
    'Jobs accessibility':'Jobs access index',
    'Land use mix ': 'Land use mix index',
}
// const attributeSelect = null
// const attributeSelectFn= getAttributes(layerSelectFn)

function getAttributes(key){
    var attributeSelectFn = "hello";
    for(const [key_attr, value_attr] of Object.entries(attributeObj)){
        console.log('in function: ',key)
        if(key == key_attr){
            attributeSelectFn = value_attr;
            break;
        }
    }
    return attributeSelectFn
};

// Add an event listener to the form submit event
form.addEventListener('submit', function(event) {
    // Get selected values from the form
    const countySelectFn= document.getElementById('countySelect').value;
    const layerSelectFn = document.getElementById('layerSelect').value;
    // const attributeSelectFn = document.getElementById('AttributeSelect').value;

        event.preventDefault(); // Prevent the default form submission

        loadingScreen.style.display = 'flex';
        // Construct the data object to be sent
        const data = {
            countySelect:countySelectFn,
            layerSelect: layerSelectFn,
            attributeSelect: getAttributes(layerSelectFn),
        };
        console.log(data);
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
        .finally(() => {
            smallInfoTitle.innerText = layerSelectFn;
            // smallInfoContent.innerText = value_chosen;
            // Hide the loading screen
            for(const [key_fetch, value_fetch] of Object.entries(innerTextObjs)){
                console.log(key_fetch, layerSelectFn)
                if( layerSelectFn == key_fetch){
                    smallTextContent.innerText = value_fetch;
                    break;
                }
                else{
                    smallTextContent.innerText = "Comming Soon, Under construction!"
                }
            }

            loadingScreen.style.display = 'none';
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


const that_fucking_card = document.querySelector('.small-info')

function showQueryLayer() {
    document.getElementById('query-layer').classList.remove('visually-hidden');
}

function hideQueryLayer() {
    document.getElementById('query-layer').classList.add('visually-hidden');
}

function removeSmallInfo(){
    that_fucking_card.classList.add('visually-hidden');
}

closeQuery.addEventListener('click', ()=>{
    setTimeout( addSmallInfo,1000);
});

function addSmallInfo(){
    that_fucking_card.classList.remove('visually-hidden');
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
    'School accessibility': 'School access index',
    'Jobs accessibility': 'job access index',
    'Healthcare Accessibility':'Healthcare access index',
}


const landUse_layers = {

    'Land use mix': 'Land use mix index',
}


const design_layers = {
    'sdna_1500meters_2018': 'Spatial design network analysis 1.5Km',
    'sdna_1000meters_2018': 'Spatial Design Network Analysis 1km',
    'sdna_500meters_2018': 'Spatial Design Network Analysis 500m'

}

const zoning_layers ={
    'ccn_zones':' Zoning'
}

const designAttrs = ['mad1500','diva1500','len1500','hullr1500','tpbta1500','mad1000','diva1000','len1000','hullr1000','tpbta1000','mad500','diva500','len500','hullr500','tpbta500']
const accessAttrs = ["schoolacce", 'saccinddrv', 'schaccessb','saccindwlk','jobaccindx','jobacratio','accessindx','acessratio']
const entropyAttrs = ['areahex','entropy_fn']
const zoningAttrs = ['dev_1970']

const layerObjs = {
    'Destination Accessibility': accesibility_layers,
    'Design of Road Network': design_layers,
    'Diversity of Land Use': landUse_layers,
    'Zoning Policy' : zoning_layers,
}

const attrsObj = {
    'Destination Accessibility':accessAttrs,
    'Design of Road Network': designAttrs,
    'Diversity of Land Use':entropyAttrs,
    'Zoning Policy': zoningAttrs,
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
                var newElement = `<option value="${key}" title="${value}">${key}</option>`
                layerSelector.insertAdjacentHTML( 'beforeend', newElement );
            };
        };
    };
}

function getCounties(){
    clearChildrenFromIndex(layerSelector,1)
    countiesOfKenya.forEach((county)=>{
        var newElement = `<option value=${county} title="${county}">${county}</option>`
        countySelector.insertAdjacentHTML('beforeend', newElement )
    });
}

const smallInfoTitle = document.querySelector(".small-info-title");
const smallInfoContent = document.querySelector(".small-info-content");

maps.forEach((map)=>{
    console.log(map)
    map.addEventListener('click',()=>  {
        var name = map.text
        console.log("name" , name)
        layerTitle.innerText = name
        const chosen_value = name
        for(const [key_chosen, value_chosen] of Object.entries(texts_objs)){
            console.log("value chosen: ",chosen_value + "\n" + "key Value: ",key_chosen)
            chosen_value == key_chosen
            if( chosen_value == key_chosen){
                expanationText.innerText = value_chosen;
                break;
            }
            else{
                expanationText.innerText = "Comming Soon, Under construction!"
            }
        }
        getCounties()
        getLayernames(layerTitle)
        // getAttrbutes(layerTitle)
    });
    clearChildrenFromIndex(layerSelector,1)
});


//Click here to see our methodology section to understand the science of measuring service accessibility.
const Accessibility_txt = "The accessibility map tells us how easy it is to access various services such as schools, jobs, and hospitals across the city. Select the layer of interest,  e.g Schools, to view the map of school accessibility. Click on a point in this interactive map to view the accessibility index. A high index number means that it is easier to access services, while a low index number means that it is more difficult to access services."
const Diversity_txt = "This map tells us how different land uses are mixed in a location. A high value means that there are more land uses mixed in a given location, while a low value tells us there is little or no mix of land uses. In your mtaa, a high value of diversity would for instance tell you that the land uses such as residential, are mixed with other land uses such as commercial."
const Density_txt = "Building density tells us the level of development in a neighborhood. It represents the number of buildings per unit area of land."
const distance_to_pt_txt = "This map shows us how far (or near) buildings are to public transport stops. "
const design_of_road_network_txt = "This map shows us how the road network is designed and how this design affects accessibility, walkability, and sustainable transport"

const drn_txt_extra = `Layer name:
Important roads
Road importance
[Roads with a high value are more  important, have more flows and are crucial to connectivity in the neighborhood ]
2. Nearness  of  places (hubs)
Nearness
[Points with  high values of nearness  are the nearest to reach from all corners of the neighborhood, they are central places ]

3. Junctions within 1 kilometer radius
Number of junctions
[This map shows us pedestrian friendly places that can promote walking and healthy lifestyly. The more junctions a place has the easier it is to navigate ]

4. Convex Hull Shape Index within 1 kilometer radius
Hull Shape Index
[This map shows us the efficiency of the road network in terms of how easy it is to navigate and move around the neighburhood. A low value is good , meaning the network is circular and one can easily reach the different places withn 1 kilometer radius)

`

const innerTextObjs = {
    'Jobs accessibility': Accessibility_txt,
    'School accessibility': Accessibility_txt,
    "Healthcare Accessibility": Accessibility_txt,
    "Land Use Mix": Diversity_txt,
    'sdna_1500meters_2018':design_of_road_network_txt,
    'sdna_1000meters_2018':design_of_road_network_txt,
    'sdna_500meters_2018': design_of_road_network_txt,
}

const texts_objs ={
    'Destination Accessibility':Accessibility_txt,
    'Diversity of Land Use':Diversity_txt,
    'Density of Buildings':Density_txt,
    'Design of Road Network': design_of_road_network_txt,
    'Distance to Public Transport': distance_to_pt_txt,
}

const closeBtn = document.getElementById('close-button');
const commentSection = document.querySelector('.comments-section');
const message_tag = document.querySelector('.messages')
closeBtn.addEventListener('click',() =>{
        commentSection.style.display = "none";
});

const commentSectionObjTitle = document.querySelector(".title-name");
// Function to open the comment section
function openCommentBox(data) {
    console.log("openCommentBox function called"); // Debugging log

    const commentBox = document.querySelector('.comments-section');
    if (commentBox) {
        commentBox.classList.add('show');
    }

    var commentSection = document.getElementById('comments-section');
    if (commentSection) {
        commentSectionObjTitle.innerText = data;
        fetch(`/getandcreatesatistisfaction/?title=${encodeURIComponent(data)}`).then(response => response.json()).then(data => {
        comments = data.comments;
        if(comments != []){
            console.log('data:', data)
            clearChildrenFromIndex(message_tag,1)
            comments.forEach((comment) =>{
                    var newElement = `
                    <div class="comment-tag bg-primary rounded m-2">
                        <h6 class="commenters-name m-2 pt-3">Mtaa wetu User</h6>
                        <p class="comment-body m-2">${comment[0]}</p>
                        <small class="ms-5 text-sm">
                            - Posted on
                            <span><i>${new Date(comment[1]).toLocaleString()}</i></span>
                        </small>
                    </div>
                    `
                    message_tag.insertAdjacentHTML('afterbegin', newElement )
                });
            }
        else{
            message_tag.innerHTML =`
                        <div class="comment-tag bg-primary rounded m-2">
                        <h6 class="commenters-name m-2 pt-3">Devs</h6>
                        <p class="comment-body m-2">Comments will show here</p>
                        <small class="ms-5 text-sm">
                            - Posted on
                            <span><i>Mon Jun 17 2:35 pm</i></span>
                        </small>
                    </div>`
        }
    });

        commentSection.style.display = 'flex';
    } else {
        console.log("Comment section not found"); // Debugging log
    }
}

// Add an event listener to listen for messages from the iframe
window.addEventListener('message', function(event) {
    console.log("Message received:", event.data); // Debugging log
    if (event.data.action === 'openCommentBox') {
        openCommentBox(event.data.data);
    }
});


document.getElementById('satisfaction-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const satisfaction = document.getElementById('satisfactionSlider').value;
    const comment = document.getElementById('Textarea').value;
    const name = commentSectionObjTitle.textContent;

    fetch('/getandcreatesatistisfaction/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            name:name,
            satisfaction: satisfaction,
            comment: comment,

        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Form submitted successfully!');
            // Optionally, you can reset the form or handle success further
        } else {
            alert('Error submitting form. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    });
});

document.getElementById('close-comment-btn').addEventListener('click', function() {
    // Handle the close button action (e.g., hide the form or modal)
});











// const draggableSection = document.getElementById('draggableSection');

// draggableSection.addEventListener('dragstart', function (e) {
//     e.dataTransfer.setData('text/plain', null);
//     const rect = e.target.getBoundingClientRect();
//     e.dataTransfer.setData('offsetX', e.clientX - rect.left);
//     e.dataTransfer.setData('offsetY', e.clientY - rect.top);
// });

// document.addEventListener('dragover', function (e) {
//     e.preventDefault();
// });

// document.addEventListener('drop', function (e) {
//     e.preventDefault();
//     const offsetX = e.dataTransfer.getData('offsetX');
//     const offsetY = e.dataTransfer.getData('offsetY');
//     draggableSection.style.position = 'absolute';
//     draggableSection.style.left = `${e.clientX - offsetX}px`;
//     draggableSection.style.top = `${e.clientY - offsetY}px`;
// });




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
  add in the overlay for neighbourhoods (done)
  separate the reseach papers
  list of papers
  datasets our datsets ()
  open linksto open data
  scrapped data inder datasets
  Themes {accessibility opportunity , network analiys properties, zoning }(Done)

   sdna = [ mad(clossness centarlity)  diva(sevierance/ separation) len(density) halr(efficiency) tpbta(2 faced-betweenness centrality) ] 1500 = 1.5 killomitres

   density , design(sdna),  opportunity , diversity(entropy), acceccibitlity, distance to public transport , population density
   short description of the layers i.e dates of aquiry for the hospitals ,
   send a layer with shops, mpesa but for now use the ones from OSM


   have a menu where people choose what the person is satisfied and uncertisfied with.
   so that people in the medical or whatever field to have better services.

   have a closed ended and open ended approach to facilities(level of satisfaction)

   feedback- contact page


 */
