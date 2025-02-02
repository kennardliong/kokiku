const imageUpload = document.getElementById('imageUpload');
const analyzeButton = document.getElementById('analyzeButton');
const resultsDiv = document.getElementById('results');
const loadingDiv = document.getElementById('loading');
const ingredientList = document.getElementById('ingredientList');
const errorDiv = document.getElementById('error');
const recipeTitle = document.getElementById("recipeTitle");
const recipeDescription = document.getElementById("recipeDescription");

let base64Image = null;

imageUpload.addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            base64Image = e.target.result.split(',')[1]; // Get Base64 data
            analyzeButton.disabled = false;
        };
        reader.readAsDataURL(file);
    }
});

analyzeButton.addEventListener('click', async () => {
    loadingDiv.classList.remove('hidden');
    resultsDiv.classList.add('hidden');
    errorDiv.classList.add('hidden');
    ingredientList.innerHTML = "";
    try {
        console.log("Making the request to /analyze-image");
         const response = await fetch("/analyze-image", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({image: base64Image})
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
        
         if (data.recipe){
            recipeTitle.classList.remove("hidden");
            recipeDescription.classList.remove("hidden")
            recipeDescription.textContent = data.recipe.description
            recipeTitle.textContent = "Possible Recipe: " + data.recipe.title
         }


    } catch (err) {
        console.error("Fetch Error:", err);
        errorDiv.textContent = "Failed to analyze image." + err.message;
        errorDiv.classList.remove('hidden');
    } finally {
        loadingDiv.classList.add('hidden');
    }
});