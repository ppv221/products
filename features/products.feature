Feature: The product service back-end
    As a Products Service Owner
    I need a RESTful catalog service
    So that I can keep track of all my products

	
Background:
    Given the following products
        | id | name       | category 	| price |  description			| color | count |
        |  1 | Flip Phone | Phone    	| 300   |  flip					| Blue  | 5     |
        |  2 | GE4509     | Microwave	| 45    |  Open Box				| Black | 12    |	
        |  3 | Moto X4    | Phone    	| 300   |  Latest Moto Phone	| Black | 8     |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Product Catalog RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Product
    When I visit the "Home Page"
    And I set the "Name" to "Flip Phone"
    And I set the "Category" to "Phone"
	And I set the "Price" to "300"
	And I set the "Count" to "5"
	And I set the "Color" to "Blue"
	And I set the "Description" to "flip"
    And I press the "Create" button
    Then I should see the message "Success"

Scenario: List all products
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "Flip Phone" in the results
    And I should see "GE4509" in the results
    And I should see "Moto X4" in the results

Scenario: List all categories
    When I visit the "Home Page"
    And I set the "Category" to "Phone"
    And I press the "Search" button
    Then I should see "Flip Phone" in the results
    And I should see "Moto X4" in the results

Scenario: Update a Product
    When I visit the "Home Page"
    And I set the "Id" to "1"
    And I press the "Retrieve" button
    Then I should see "Flip Phone" in the "Name" field
    When I change "Name" to "samsung8"
    And I press the "Update" button
    Then I should see the message "Success"
    When I set the "Id" to "1"
    And I press the "Retrieve" button
    Then I should see "samsung8" in the "Name" field
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see "samsung8" in the results
    Then I should not see "Flip Phone" in the results
