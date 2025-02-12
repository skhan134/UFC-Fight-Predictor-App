 // Function to fetch fighters based on division from the API
function fetchFighters(division) {
  fetch(`/api/fighters/${division}`)
      .then(response => response.json())
      .then(fighters => populateFighterDropdown(fighters))
      .catch(error => console.error("Error fetching fighters:", error));
}

// Function to populate the dropdowns with the fetched fighters
function populateFighterDropdown(fighters) {
  const fighter1Search = document.getElementById("fighter1-search");
  const fighter2Search = document.getElementById("fighter2-search");
  const fighter1List = document.getElementById("fighter1-list");
  const fighter2List = document.getElementById("fighter2-list");

  // Clear existing fighters in dropdowns
  fighter1List.innerHTML = "";
  fighter2List.innerHTML = "";

  // Create and append fighter options to the dropdown lists
  fighters.forEach(fighter => {
      const fighter1Option = document.createElement("li");
      fighter1Option.textContent = fighter;
      fighter1Option.onclick = () => selectFighter(fighter, "fighter1");
      fighter1List.appendChild(fighter1Option);

      const fighter2Option = document.createElement("li");
      fighter2Option.textContent = fighter;
      fighter2Option.onclick = () => selectFighter(fighter, "fighter2");
      fighter2List.appendChild(fighter2Option);
  });

  // Add event listener to search inputs
  fighter1Search.addEventListener("input", () => filterFighters(fighter1Search, fighter1List));
  fighter2Search.addEventListener("input", () => filterFighters(fighter2Search, fighter2List));
}

// Function to filter fighters based on search input
function filterFighters(searchInput, list) {
  const searchQuery = searchInput.value.toLowerCase();
  const options = list.getElementsByTagName("li");

  // Loop through all the list items and hide those that don't match the search query
  Array.from(options).forEach(option => {
      const text = option.textContent.toLowerCase();
      if (text.includes(searchQuery)) {
          option.style.display = "block";  // Show matched options
      } else {
          option.style.display = "none";  // Hide unmatched options
      }
  });
}

// Function to select a fighter from the dropdown
function selectFighter(fighter, dropdownId) {
  const fighterInput = document.getElementById(`${dropdownId}-search`);
  fighterInput.value = fighter;  // Set the search input value to the selected fighter

  // Hide the dropdown list after selection
  const fighterList = document.getElementById(`${dropdownId}-list`);
  fighterList.style.display = "none";
}

// Function to toggle dropdown visibility when clicked
function toggleDropdown(dropdownId) {
  const fighterList = document.getElementById(`${dropdownId}-list`);
  fighterList.style.display = fighterList.style.display === "none" || fighterList.style.display === "" ? "block" : "none";
}

// Add event listeners to search inputs to toggle dropdown visibility
document.getElementById("fighter1-search").addEventListener("click", function() {
  toggleDropdown("fighter1");
});

document.getElementById("fighter2-search").addEventListener("click", function() {
  toggleDropdown("fighter2");
});

// Add event listeners to search inputs for filtering fighters
document.getElementById("fighter1-search").addEventListener("input", function() {
  filterFighters(this, document.getElementById("fighter1-list"), "fighter1");
});

document.getElementById("fighter2-search").addEventListener("input", function() {
  filterFighters(this, document.getElementById("fighter2-list"), "fighter2");
});

// Example: Populate dropdowns when a division is selected
document.getElementById("division").addEventListener("change", function () {
  const selectedDivision = this.value;
  fetchFighters(selectedDivision);
});

// Function to make the prediction API call
function predictMatchup() {
  const fighter1 = document.getElementById('fighter1-search').value;
  const fighter2 = document.getElementById('fighter2-search').value;

  if (!fighter1 || !fighter2) {
      document.getElementById('prediction-result').innerHTML = 'Please select both fighters!';
      return;
  }

  // Prepare the request data
  const requestData = {
      fighter1: fighter1,
      fighter2: fighter2
  };

  // Make the API call to your Flask backend for prediction
  fetch('/predict', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
  })
  .then(response => response.json())
  .then(data => {
      // Handle the prediction result
      if (data.error) {
          document.getElementById('prediction-result').innerHTML = `Error: ${data.error}`;
      } else {
          const winner = data;
          document.getElementById('prediction-result').innerHTML = `${winner} is predicted to win!`;
      }
  })
  .catch(error => {
      document.getElementById('prediction-result').innerHTML = 'Error predicting the match!';
      console.error('Error:', error);
  });
}
  