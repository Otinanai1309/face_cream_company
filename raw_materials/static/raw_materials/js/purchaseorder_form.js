function createPurchaseOrderData() {
  let formData = new FormData($('#purchase-order-form')[0]);
  $('.order-line-form').each(function(index) {
      $(this).find('input, select').each(function() {
          formData.append(this.name, this.value);
      });
  });
  return formData;
}

let isSubmitting = false;

function submitPurchaseOrder(e) {
  if (isSubmitting) return;
  isSubmitting = true;
  e.preventDefault();

  $.ajax({
    url: $('#purchase-order-form').attr('action'),
    type: 'POST',
    data: createPurchaseOrderData(),
    processData: false,
    contentType: false,
    headers: {
        'X-Requested-With': 'XMLHttpRequest'
    },
    success: function(response) {
        if (response.success) {
            alert('Purchase order created successfully!');
            window.location.href = response.url;
        } else {
            alert('There were errors in your submission. Please check the form and try again.');
            console.log(response.form_errors);
            console.log(response.line_errors);
        }
    },
    error: function(xhr, status, error) {
        alert('An error occurred while creating the purchase order.');
        console.error(error);
    }
})
.always(function() {
    isSubmitting = false;
});
  
}


$(document).ready(function() {
  $("#purchase-order-form").submit(submitPurchaseOrder);
});
