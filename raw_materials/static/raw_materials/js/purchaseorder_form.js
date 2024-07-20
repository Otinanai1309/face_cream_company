$(document).ready(function() {
    data: createPurchaseOrderData(),
    success: function(data) {
      alert('Purchase order created successfully!');
      window.location.href = "{% url 'purchaseorder_list' %}";
    },
    error: function(xhr, status, error) {
      alert('An error occurred while creating the purchase order.');
      console.error(error);
    }
  });
});
}

$(document).ready(function() {
  $("#purchase-order-form").submit(submitPurchaseOrder);
});
