$(function () {
  
    var msie6 = $.browser == 'msie' && $.browser.version < 7;
    
    if (!msie6 && $('.leftsidebar').offset()!=null) {
      var top = $('.leftsidebar').offset().top - parseFloat($('.leftsidebar').css('margin-top').replace(/auto/, 0));
      var height = $('.leftsidebar').height();
      var winHeight = $(window).height();	
      var footerTop = $('#footer').offset().top - parseFloat($('#footer').css('margin-top').replace(/auto/, 0));
      var gap = 7;
      $(window).scroll(function (event) {
        // what the y position of the scroll is
        var y = $(this).scrollTop();
        
        // whether that's below the form
        if (y+winHeight >= top+ height+gap && y+winHeight<=footerTop) {
          // if so, ad the fixed class
          $('.leftsidebar').addClass('leftsidebarfixed').css('top',winHeight-height-gap +'px');
        } 
        else if (y+winHeight>footerTop) {
          // if so, ad the fixed class
         $('.leftsidebar').addClass('leftsidebarfixed').css('top',footerTop-height-y-gap+'px');
        } 
        else 	  
        {
          // otherwise remove it
          $('.leftsidebar').removeClass('leftsidebarfixed').css('top','0px');
        }
      });
    }  
  });