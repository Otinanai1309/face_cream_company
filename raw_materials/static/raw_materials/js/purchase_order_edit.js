document.addEventListener('DOMContentLoaded', function() {
  const orderLinesTable = document.getElementById('order-lines');
  const addLineButton = document.getElementById('add-line');

  addLineButton.addEventListener('click', addNewLine);
  orderLinesTable.addEventListener('click', handleRemoveLine);
  orderLinesTable.addEventListener('change', handleInputChange);

  function addNewLine() {
      const newRow = orderLinesTable.insertRow(-1);
      newRow.innerHTML = `
          <td>
              <select name="raw_material" class="raw-material-select">
                  <!-- Add options dynamically using AJAX or include all options here -->
              </select>
          </td>
          <td><input type="number" name="quantity" class="quantity-input"></td>
          <td><input type="number" name="price" class="price-input" step="0.01"></td>
          <td><input type="number" name="cost" class="cost-input" readonly></td>
          <td><input type="number" name="vat" class="vat-input" readonly></td>
          <td><button type="button" class="remove-line">Remove</button></td>
      `;
  }

  function handleRemoveLine(event) {
      if (event.target.classList.contains('remove-line')) {
          event.target.closest('tr').remove();
          updateTotals();
      }
  }

  function handleInputChange(event) {
      if (event.target.classList.contains('quantity-input') || 
          event.target.classList.contains('price-input')) {
          updateLineTotals(event.target.closest('tr'));
      }
  }

  function updateLineTotals(row) {
      const quantity = parseFloat(row.querySelector('.quantity-input').value) || 0;
      const price = parseFloat(row.querySelector('.price-input').value) || 0;
      const cost = quantity * price;
      const vat = cost * 0.24; // Assuming 24% VAT, adjust as needed

      row.querySelector('.cost-input').value = cost.toFixed(2);
      row.querySelector('.vat-input').value = vat.toFixed(2);

      updateTotals();
  }

  function updateTotals() {
      let totalCost = 0;
      let totalVat = 0;

      orderLinesTable.querySelectorAll('tbody tr').forEach(row => {
          totalCost += parseFloat(row.querySelector('.cost-input').value) || 0;
          totalVat += parseFloat(row.querySelector('.vat-input').value) || 0;
      });

      document.getElementById('total_cost').value = totalCost.toFixed(2);
      document.getElementById('total_vat').value = totalVat.toFixed(2);
  }
});