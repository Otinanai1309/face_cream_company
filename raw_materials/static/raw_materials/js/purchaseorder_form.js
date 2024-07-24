function createPurchaseOrderData() {
    let formData = new FormData($('#purchase-order-form')[0]);
    
    // Append data from each order line form
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
  
    // Validate form data before submission
    if (!validateForm()) {
      isSubmitting = false;
      return;
    }
  
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
  
  function validateForm() {
    let isValid = true;
    // Add your form validation logic here
    // For example, check if required fields are filled
    $('#purchase-order-form').find('input, select').each(function() {
      if ($(this).prop('required') && !$(this).val()) {
        isValid = false;
        $(this).addClass('is-invalid');
      } else {
        $(this).removeClass('is-invalid');
      }
    });
    return isValid;
  }
  
  $(document).ready(function() {
    $("#purchase-order-form").submit(submitPurchaseOrder);
  });