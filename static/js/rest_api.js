$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) 
    {
        $("#product_id").val(res.id);
        $("#product_name").val(res.name);
        $("#product_category").val(res.category);
		$("#product_price").val(res.price);
		$("#product_color").val(res.color);
		$("#product_count").val(res.count);
		$("#product_description").val(res.description);
       /*  if (res.id) 
        {
            $("#product_id").val("res.id");
        } 
        else 
        {
            $("#product_available").val("false");
        } */
    }

    /// Clears all form fields
    function clear_form_data() {
		$("#product_name").val("");
        $("#product_category").val("");
		$("#product_price").val("");
		$("#product_color").val("");
		$("#product_count").val("");
		$("#product_description").val("");
        
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Product
    // ****************************************

    $("#create-btn").click(function () {

        var name = $("#product_name").val();
        var category = $("#product_category").val();
		var price = $("#product_price").val();
		var color = $("#product_color").val();
		var count = $("#product_count").val();
		var description =$("#product_description").val();
       // var available = $("#product_available").val() == "true";

        var data = {
            "name": name,
            "category": category,
            "color": color,
			"price": price,
			"count": count,
			"description": description
			
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/products",
            contentType:"application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Great Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Product
    // ****************************************

    $("#update-btn").click(function () {

        var product_id = $("#product_id").val();
        var name = $("#product_name").val();
        var category = $("#product_category").val();
        var price = $("#product_price").val();
		var color = $("#product_color").val();
		var count = $("#product_count").val();
		var description =$("#product_description").val();

        var data = {
            "name": name,
            "category": category,
            "color": color,
			"price": price,
			"count": count,
			"description": description
        };

        var ajax = $.ajax({
                type: "PUT",
                url: "/products/" + product_id,
                contentType:"application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Great Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Product
    // ****************************************

    $("#retrieve-btn").click(function () {

        var product_id = $("#product_id").val();
        var count = $("#product_count").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/products/" + product_id,
            contentType:"application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Great Success,let's have fun")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    $("#add-unit-btn").click(function () 
    {

        var product_id = $("#product_id").val();

        var ajax = $.ajax({
            type: "PUT",
            url: "/products/" + product_id + "/add_unit",
            contentType:"application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Great Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    $("#sell-unit-btn").click(function () 
    {

        var product_id = $("#product_id").val();

        var ajax = $.ajax({
            type: "PUT",
            url: "/products/" + product_id + "/sell_products",
            contentType:"application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Great Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Product
    // ****************************************

    $("#delete-btn").click(function () {

        var product_id = $("#product_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/products/" + product_id,
            contentType:"application/json",
            data: '',
        })

        // flash_message("Product with ID [" + res.id + "] has been Deleted!")
        
        ajax.done(function(res){
            clear_form_data()
            // flash_message("Product with ID [" + res.id + "] has been Deleted!")
            // flash_message("Product with ID 5 has been Deleted!")
            flash_message("Product has been deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#product_id").val("");
        clear_form_data()
    });

    // ****************************************
    // Search for a Product
    // ****************************************

    $("#search-btn").click(function () 
    {

        var name = $("#product_name").val();
        var category = $("#product_category").val();
        var price = $("#product_price").val();
		var color = $("#product_color").val();
		var count = $("#product_count").val();
		var description =$("#product_description").val();

        var queryString = ""

        if (name) {
            queryString += 'name=' + name
        }
        if (category) {
            if (queryString.length > 0) {
                queryString += '&category=' + category
            } else {
                queryString += 'category=' + category
            }
        }
		
		/* if (price) {
            queryString += 'price=' + price
        }
		
		if (color) {
            queryString += 'color=' + color
        }
		
		if (count) {
            queryString += 'count=' + count
        }
		if (description) {
            queryString += 'description=' + description
        } */
		
		
       // if (available) {
       //     if (queryString.length > 0) {
       //         queryString += '&available=' + available
       //     } else {
       //         queryString += 'available=' + available
       //     }
       // }

        var ajax = $.ajax({
            type: "GET",
            url: "/products?" + queryString,
            contentType:"application/json",
            data: ''
        })

        ajax.done(function(res)
        {
            //alert(res.toSource())
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped">');
            var header = '<tr>'
            header += '<th style="width:10%">ID</th>'
            header += '<th style="width:40%">Name</th>'
            header += '<th style="width:40%">Category</th>'
			header += '<th style="width:40%">Color</th>'
			header += '<th style="width:40%">Price</th>'
			header += '<th style="width:40%">Count</th>'
            header += '<th style="width:10%">Description</th></tr>'
            $("#search_results").append(header);
            for(var i = 0; i < res.length; i++) {
                product = res[i];
                var row = "<tr><td>"+product.id+"</td><td>"+product.name+"</td><td>"+product.category+"</td><td>"+product.color+"</td><td>"+product.price+"</td><td>"+product.count+"</td><td>"+product.description+"</td></tr>";
                $("#search_results").append(row);
            }

            $("#search_results").append('</table>');

            flash_message("Great Success")
        });

        ajax.fail(function(res)
        {
            flash_message(res.responseJSON.message)
        });

    });

})
