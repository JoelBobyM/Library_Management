function fetchSearchResults() {
    // Get the search query
    var searchQuery = $('#search-query').val();

    console.log(searchQuery);
    
    // Make an AJAX request to your Flask endpoint to fetch search results
    $.ajax({
        url: '/search-book',  // Update this to your search route
        type: 'POST',    // Use POST or GET as needed
        data: JSON.stringify({ 'search_query': searchQuery }),
        contentType: 'application/json',
        success: function(data) {
            // Clear the card container
            $('#card-container').empty();
            
            var newData = "<b> Search Result </b>";
            $('#card-title').html(newData);
            
            // Loop through the search results and add cards to the container
            for (var i = 0; i < data.length; i++) {
                var book = data[i];
                var cardHtml = '<div class="card">' +
                    '<img src="' + book.image_url + '" alt="" />' +
                    '<div class="overlay">' +
                    '<h2>' + book.title + '</h2>' +
                    '<p>' + book.status + '</p>' +
                    '</div>' +
                    '</div>';
                $('#card-container').append(cardHtml);
            }
        },
        error: function(error) {
            console.error('Error:', error);
        }
    });
}

function populateirTable(selectedTab,data) 
{
    if (selectedTab === "ir_full")
    {
        var tableBody = document.getElementById("irfull_tab_body");
    }
    else if(selectedTab === "ir_act")
    {
        var tableBody = document.getElementById("iract_tab_body");
    }
    else if(selectedTab === "ir_stud_full")
    {
        var tableBody = document.getElementById("ir_studfull_tab_body");
    }
    else if (selectedTab === "ir_stud_act")
    {
        var tableBody = document.getElementById("ir_studact_tab_body");
    }

    tableBody.innerHTML = "";

    data.forEach(function (book) 
    {
        console.log(data)
        var row = document.createElement("tr");

        var titleCell = document.createElement("td");
        titleCell.textContent = book.Title;

        var issueCell = document.createElement("td");
        issueCell.textContent = book.Issue_Date;

        var issue_id = document.createElement("td");
        issue_id.textContent = book.Issue_ID;

        var dueCell = document.createElement("td");
        dueCell.textContent = book.Due_Date;

        var dateString = book.Due_Date;
        var parts = dateString.split('-');
        var dueDate = new Date(parts[2], parts[1] - 1, parts[0]);

        var currentDate = new Date();

        console.log(dueDate);

        if ((selectedTab === "ir_full")||(selectedTab === "ir_stud_full"))
        {
            if ((dueDate < currentDate)&&(book.Return_Date === "N/A")) 
            {
                row.style.backgroundColor = "red";
            }
        }
        else if ((selectedTab === "ir_act")||(selectedTab === "ir_stud_act"))
        {
            if (dueDate < currentDate)
            {
                row.style.backgroundColor = "red";
            }
        }
        
        if ((selectedTab === "ir_full")||(selectedTab === "ir_act"))
        {

            
            var admissionCell = document.createElement("td");
            admissionCell.textContent = book.Admission_Number;

            var nameCell = document.createElement("td");
            nameCell.textContent = book.S_Name;

            // Append cells to the row
            row.appendChild(issue_id);
            row.appendChild(admissionCell);
            row.appendChild(nameCell);
            row.appendChild(titleCell);
            row.appendChild(issueCell);
            row.appendChild(dueCell);

            if(selectedTab == "ir_full")
            {
                var returnCell = document.createElement("td");
                returnCell.textContent = book.Return_Date;
                row.appendChild(returnCell);
            }
        }
        else if ((selectedTab === "ir_stud_full")||(selectedTab === "ir_stud_act"))
        {
            row.appendChild(issue_id);
            row.appendChild(titleCell);
            row.appendChild(issueCell);
            row.appendChild(dueCell);

            if(selectedTab == "ir_stud_full")
            {
                var returnCell = document.createElement("td");
                returnCell.textContent = book.Return_Date;
                row.appendChild(returnCell);
            }
        }
        
        tableBody.appendChild(row);
    });
}


function fetch_ir_data(selectedTab) 
{
    console.log('Selected Tab:', selectedTab);
    var admn_no =  sessionStorage.getItem('admn_no');
    $.ajax(
    {
        url: '/ir_data',
        type: 'POST',
        data: JSON.stringify({ 'selected_tab': selectedTab, 'admn_no' : admn_no }),
        contentType: 'application/json',
        success: function(data) 
        {
            populateirTable(selectedTab,data);
        },
        error: function(error) 
        {
            console.error('Error:', error);
        }
    });
}



$(document).ready(function() 
{
    if ($('#loggedin').length > 0) 
    { 
        fetch_ir_data('ir_act'); 
        fetch_ir_data('ir_full'); 
    }

    if ($('#loggedinstud').length > 0) 
    {  
        fetch_ir_data('ir_stud_act'); 
        fetch_ir_data('ir_stud_full'); 
    }

    // Add an event listener for the search button
    $('#search-button').click(function() 
    {
        // Call the fetchSearchResults function when the button is clicked
        fetchSearchResults();
    });

    // Add an event listener for the radio buttons
    $('input[type="radio"]').change(function() 
    {
        // Get the ID of the selected radio button
        var selectedTab = $(this).attr('id');
        
        // Call your JavaScript method with the selectedTab as a parameter
        fetch_ir_data(selectedTab);
    });


    var admn_no =  sessionStorage.getItem('admn_no');
    
    // Make an AJAX request to fetch student details
    $.ajax({
        url: '/get_stud_det',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ 'admission_number': admn_no }),
        success: function(data) 
        {
            console.log(data);
            // Update the my_name variable with the student's name
            var myNameElement = document.getElementById('my_name');
            myNameElement.innerHTML = data.Name + ' <span class="material-symbols-outlined"> person </span> ';
        },
        error: function(error) {
            console.error('Error:', error);
        }
    });
});
