const imageUpload = document.getElementById('imageUpload');
const analyzeButton = document.getElementById('analyzeButton');
const resultsDiv = document.getElementById('results');
const loadingDiv = document.getElementById('loading');
const ingredientList = document.getElementById('ingredientList');
const errorDiv = document.getElementById('error');
const recipeTitle = document.getElementById("recipeTitle");
const recipeDescription = document.getElementById("recipeDescription");
const recipeList = document.getElementById('recipeList');
const imagePreview = document.getElementById('imagePreview');
const imageUploadContainer = document.getElementById("imageUploadContainer");
const mealTypeSelect = document.getElementById('mealType');
const cuisineSelect = document.getElementById('cuisine');
const intolerancesSelect = document.getElementById('intolerances');
const dietSelect = document.getElementById('diet');


let base64Image = null;

imageUploadContainer.style.display = "block";
// Set a default image on load
imagePreview.src = "public/pantry.jpg";
imagePreview.style.display = "block";

imageUpload.addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            base64Image = e.target.result.split(',')[1]; // Get Base64 data
            imagePreview.src = e.target.result;
            imagePreview.style.display = "block";
            analyzeButton.disabled = false;
        };
        reader.readAsDataURL(file);
    }
});

analyzeButton.addEventListener('click', async () => {
    loadingDiv.classList.remove('hidden');
    resultsDiv.classList.add('hidden');
    errorDiv.classList.add('hidden');
     recipeList.innerHTML = "";
    ingredientList.innerHTML = "";

    try {
        console.log("Making the request to /analyze-image");
         const selectedMealType = mealTypeSelect.value;
        const selectedCuisine = cuisineSelect.value;
        const selectedIntolerances = intolerancesSelect.value;
        const selectedDiet = dietSelect.value;


        const response = await fetch("/analyze-image", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
             body: JSON.stringify({
                image: base64Image,
                mealType: selectedMealType,
                cuisine: selectedCuisine,
                intolerances: selectedIntolerances,
                diet: selectedDiet,
            })
        })
         console.log("Received the response from /analyze-image");

      const data = await response.json();
        console.log("Response Json:", data);

        if(data.error){
            console.error("Server error", data.error);
            errorDiv.textContent = data.error
            errorDiv.classList.remove('hidden');
              loadingDiv.classList.add('hidden');
            return
        }

        if (data.ingredients && data.ingredients.length > 0) {
            data.ingredients.forEach(ingredient => {
                let li = document.createElement("li")
                li.textContent = ingredient.trim();
                ingredientList.appendChild(li);
            });
          resultsDiv.classList.remove('hidden');

        } else {
             errorDiv.textContent = "No ingredients or data detected."
            errorDiv.classList.remove('hidden');
        }

        if (data.recipes && data.recipes.length > 0) {

            let recipeRow = null;

            data.recipes.forEach((recipe, index) => {

                if (index % 4 === 0) {
                    recipeRow = document.createElement("div");
                    recipeRow.classList.add("row", "justify-content-center");
                  recipeList.appendChild(recipeRow);
               }


              let jumbotron = document.createElement("div");
              jumbotron.classList.add("jumbotron", "mb-3", "col-md-3", "text-center",  "recipe-card"); // Add Bootstrap classes
              let h2 = document.createElement("h2");
               h2.textContent = recipe.title;
              let a = document.createElement("a");
                a.href = `/recipe/${recipe.id}`;
               let img = document.createElement("img");
               img.src = recipe.image;
               img.style.width = "100%";
               img.style.maxWidth = "200px";
                img.style.height = "auto";
               a.appendChild(img)
              jumbotron.appendChild(a)
                jumbotron.appendChild(h2)
                if(recipeRow){
                     recipeRow.appendChild(jumbotron);
                 }

             });
        }

        } catch (err) {
        console.error("Fetch Error:", err);
        errorDiv.textContent = "Failed to analyze image." + err.message;
        errorDiv.classList.remove('hidden');
    } finally {
        loadingDiv.classList.add('hidden');
    }
});
