// Currently not implemented. This code needs to be modified to work with the menu page.
function loadExploreContent(category) {
    console.log(category);
    let user_url = `/category/${category}`;
    console.log(user_url);
    fetch(user_url)
      .then(response => response.json())
      .then(data => {
        const artworkContainer = document.querySelector('.artwork-grid');
        while (artworkContainer.firstChild) {
          artworkContainer.removeChild(artworkContainer.firstChild);
        }
        console.log(data);
        //Create items
        for (let key in data) {
          createExploreThumbnail(data[key], artworkContainer);
          console.log(data[key]);
  
        }
      });
  }