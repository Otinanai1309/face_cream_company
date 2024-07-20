// Test cases for the purchaseorder_form.js file

// Test case for the createPurchaseOrderData function
function testCreatePurchaseOrderData() {
    // Setup test data
    const formData = new FormData();
    formData.append('key1', 'value1');
    formData.append('key2', 'value2');

    const orderLines = [
        { raw_material_id: 1, quantity: 10, price: 5.99 },
        { raw_material_id: 2, quantity: 20, price: 3.99 }
    ];

    // Call the function
    const result = createPurchaseOrderData();

    // Check the result
    const expectedResult = {
        key1: 'value1',
        key2: 'value2',
        order_lines: orderLines
    };
    assert.deepEqual(result, expectedResult, 'createPurchaseOrderData should return the correct data');
}

// Test case for the calculateTotals function
function testCalculateTotals() {
    // Setup test data
    const orderLines = [
        { raw_material_id: 1, quantity: 10, price: 5.99 },
        { raw_material_id: 2, quantity: 20, price: 3.99 }
    ];

    // Call the function
    calculateTotals();

    // Check the result
    const expectedTotalCost = 10 * 5.99 + 20 * 3.99;
    const expectedTotalVAT = expectedTotalCost * 0.24;
    assert.equal($('#total-cost').text(), expectedTotalCost.toFixed(2), 'Total cost should be calculated correctly');
    assert.equal($('#total-vat').text(), expectedTotalVAT.toFixed(2), 'Total VAT should be calculated correctly');
}

// Run the tests
testCreatePurchaseOrderData();
testCalculateTotals();
