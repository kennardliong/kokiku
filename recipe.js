const recipeTitle = document.getElementById('recipeTitle')
const recipeImage = document.getElementById('recipeImage')
const ingredientsList = document.getElementById('ingredientsList')
const instructionsDiv = document.getElementById("instructions")

const urlParams = new URLSearchParams(window.location.search)
const recipeId =  window.location.pathname.split("/")[2]


async function fetchRecipeDetails(recipeId) {
    try {
        const response = await fetch(`/recipe-details/${recipeId}`);
        const data = await response.json();
          console.log(data);
        recipeTitle.textContent = data.title;
        recipeImage.src = data.image;


         if(data.extendedIngredients && data.extendedIngredients.length > 0){
            data.extendedIngredients.forEach(item =>{
              let li = document.createElement("li");
               li.textContent = `${item.name}: ${item.amount} ${item.unit}`;
              ingredientsList.appendChild(li)
            })
        }

       if (data.instructions && Array.isArray(data.instructions)) {
              let ol = document.createElement("ol");
            data.instructions.forEach((step, index) => {
                let li = document.createElement("li");
               li.textContent = step.step;
                 li.classList.add("list-group-item")
                 ol.appendChild(li);
            });
           instructionsDiv.appendChild(ol);
         } else if(data.instructions){
              instructionsDiv.textContent = data.instructions;
         }


    } catch (error) {
          console.error("Failed to fetch recipe details", error)
         recipeTitle.textContent = "Could not load recipe"
    }
}


fetchRecipeDetails(recipeId)
