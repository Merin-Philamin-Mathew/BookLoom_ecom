
// AJAX request for adding product to cart
$('.add-to-cart-btn').on('click',  function () {
  let this_val = $(this);
  let index = this_val.attr("data-index")
  let quantity = $(".product-quantity-"+_index).val();
  let product_id = $(".product-id-"+_index).val();
  let product_name = $(".product-name-"+_index).val();
  let product_slug = $(".product-slug-"+_index).val();
  let product_image = $(".product-image-"+_index).val();
  let product_price = $(".current-product-price-"+_index).text();

  console.log("index:", index);
  console.log("Quantity:", quantity);
  console.log("Title:", product_name);
  console.log("Price:", product_price);
  console.log("image:", product_image);
  console.log("Slug:", product_slug);
  console.log("ID:", product_id);
  console.log("Current Element:", this_val);

  $.ajax({
      url: 'http://127.0.0.1:8000/add-to-cart/',
      //url: "{% url 'store_app:add_to_cart' %}",
      method: 'GET',
      data: {
          'id': product_id,
          'slug': product_slug,
          'image':product_image,
          'qty': quantity,
          'title': product_name,
          'price': product_price,
          //'csrf_token': csrftoken,
      },
      dataType: 'json',
      beforeSend: function (xhr, settings) {
          // Set the CSRF token in the request headers
          //xhr.setRequestHeader('X-CSRFToken', csrftoken);
          console.log("Adding Product to Cart...");
      },
      success: function (response) {
          this_val.html("✔");
          console.log("Added Product to Cart!");
          $(".cart-items-count").text(response.totalcartitems)
      },
      error: function (xhr, status, error) {
          console.log("Error adding product to cart:", error);
      }
  });

  });