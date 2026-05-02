$(document).ready(function () {
    var widthScreen = $(window).width()
    //AOS init
    AOS.init({
        duration: 1200,
    });
    //smart menu
    $('#main-menu').smartmenus({
        mainMenuSubOffsetX: -1,
        mainMenuSubOffsetY: 4,
        subMenusSubOffsetX: 6,
        subMenusSubOffsetY: -6
    });

    //mobile menu
    var MenuMobileButton = $('.jepret-menu-mobile')
    var Menu = $('#main-menu')
    var ShowMenu = widthScreen > 768 ? true : false
    MenuMobileButton.on('click', function () {
        ShowMenu = !ShowMenu
        ShowMenu === true ? Menu.toggleClass('active') : Menu.removeClass('active')
    })

    // personal-photographer page js
    var target1 = document.getElementById('scroll-move'),
        target2 = document.getElementById('scroll-move2'),
        target3 = document.getElementById('scroll-move3')
    var height = $('.projects-block').height()
    var area = document.getElementById('mousehover')
    var range = 100

    if (target2) {
        var element_position = $('.testimonial-block').offset().top
        var screen_height = $(window).height()
        var activation_offset = 0.2
        var activation_point = element_position - (screen_height * activation_offset)
        var max_scroll_height = $('body').height() - screen_height - 5
        var initValue = widthScreen <= 1200 
            ? $('#scroll-move').offset().top / 4 
            : $('#scroll-move').offset().top / 2
        var y = widthScreen > 1440 ? '0' : initValue
        widthScreen <=768 
            ? target1.style.transform = "translateY(0px)"
            : target1.style.transform = "translateY(" + y + "px)"
        if (widthScreen > 1024) {
            target2.style.transform = "translateY(" + height + "px)"
        }
        $(window).on('scroll', function () {
            if(window.scrollY > 1) {
                y = window.scrollY / 3
            }
            var yAxis = widthScreen <= 1024
                ? (window.scrollY - height) / 20
                : (window.scrollY - height) / 5,
                offset = height / 2,
                calc = 1 - ($(this).scrollTop() - offset + range) / range
            var opacity = -calc
            if (opacity >= 1) {
                opacity = 1
            }

            if (widthScreen <= 767) {
                target3.style.transform = "translateY(0px)"
                target3.style.opacity = opacity
            } else if (widthScreen <= 1024) {
                target2.style.transform = "translateY(0px)"
                target3.style.opacity = opacity
                target3.style.transform = "translateY(" + -yAxis + "px)"
            } else {
                $('#opacity').css({ 'opacity': opacity })
                target2.style.transform = "translateY(" + -yAxis + "px)"
                target1.style.transform = "translateY(" + -y + "px)"
            }

            var y_scroll_pos = window.pageYOffset
            var element_in_view = y_scroll_pos > activation_point
            var has_reached_bottom_of_page = max_scroll_height <= y_scroll_pos && !element_in_view

            if(element_in_view || has_reached_bottom_of_page) {
                var testiScrollY = widthScreen <= 768 
                    ? (window.scrollY - $('.testimonial-block').height()) / 50
                    : (window.scrollY - $('.testimonial-block').height()) / 20
                $('#scroll-move4').css({'transform': `translateY(${-testiScrollY}px)`})
            } else {
                $('#scroll-move4').css({'transform': `translateY(0px)`})
            }
        })
    }

    if (area) {
        $('#mousehover').on('mousemove', function (e) {
            var x = (window.innerWidth / 2 - e.pageX) / 100
            var y = (window.innerHeight / 2 - e.pageY) / 100

            $('.smart-img').each(function (index) {
                var i = index + 1
                var yDirection = widthScreen <= 1024 ? y : y / 5
                var xDirection = widthScreen <= 1024 ? x : x / 5
                if (widthScreen < 768) {
                    $(`#project-item${i}`).css({
                        '--rotateX': '0deg', '--rotateY': '0deg'
                    })
                } else {
                    if (i === 1 || i === 4) {
                        $(`#project-item${i}`).css({
                            '--rotateX': `${yDirection}deg`,
                            '--rotateY': `${-xDirection}deg`
                        })
                    } else {
                        $(`#project-item${i}`).css({
                            '--rotateX': `${-yDirection}deg`, '--rotateY': `${xDirection}deg`
                        })
                    }
                }
            })
        })
    }

    $(window).on('scroll', function () {
        var yAxis = widthScreen <= 800
            ? -(window.scrollY - height) / 10
            : -(window.scrollY - height) / 5

        $('.smart-img').each(function (index) {
            var i = index + 1
            document.getElementById(`project-item${i}`).style.transform = `translateY(${yAxis}px) 
            rotateX(var(--rotateX)) rotateY(var(--rotateY))`
            if(widthScreen <= 767) {
                document.getElementById(`project-item${i}`).style.transform = `translateY(0px) 
                rotateX(var(--rotateX)) rotateY(var(--rotateY))`
            }
        })
    })

    //profesional studio page js
    if($('.intro-block').length > 0) {
        if(widthScreen > 1024) {
            var yInitValue = widthScreen <= 1440 ? $('.intro-image-wrap').offset().top / 5 : 0
            $('.intro-image-wrap').css({'transform': `translateY(${yInitValue}px)`})
        }
        $(window).on('scroll', function () {
            var scrollTop = widthScreen <= 1200 
                ? window.scrollY / 7 : window.scrollY / 5
    
            $('.intro-image-wrap').css({ 'transform': `translateY(${-scrollTop}px)`, 
            'transition-duration': '0s' })
        })
    }

    var maxOpc = 1
    var minOpc = 0
    var screenMargin = 0.2
    var element = document.querySelectorAll('.opacity1')

    function isOnScreen(el) {
        var elRects = el.getClientRects()[0]
        var winHeight = window.innerHeight
        var topIsOnScreen = elRects.top < winHeight * (1 - screenMargin)
        var bottomIsOnScreen = elRects.bottom > winHeight * screenMargin

        return topIsOnScreen && bottomIsOnScreen
    }

    function update() {
        element.forEach((element) => {
            var opacity = minOpc
            if (isOnScreen(element)) {
                opacity = maxOpc
            }
            element.style.opacity = opacity
        })

        window.requestAnimationFrame(update)
    }

    function init() {
        document.querySelector('body').classList.add('js')
        update()
    }
    init()

    //landing slider page
    var swiper = new Swiper(".mySwiper", {
        spaceBetween: 30,
        effect: "fade",
        loop: true,
        autoplay: {
            delay: 5000,
        },
        navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
        },
        pagination: {
            el: ".swiper-pagination",
            clickable: true,
        },
    });

    //gallery adora
    var swiper = new Swiper(".adora-swiper", {
        spaceBetween: 20,
        loop: true,
        centeredSlides: true,
        navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
        },
        allowTouchMove: true,
        breakpoints: {
            641: {
                slidesPerView: 2
            },
            1024: {
                slidesPerView: 2,
                spaceBetween: 30,
            },
            1200: {
                slidesPerView: 3
            }
        }
    });

    var state = false
    $('.adora-button').on('click', function () {
        state = !state
        state === true ?
            $('.adora-contcept-block').toggleClass('view-item-active')
            : $('.adora-contcept-block').removeClass('view-item-active')
    })

    $('.item-wrap').lightGallery({
        thumbnail: false
    })

    //gallery-grid & gallery masonry
    var wrapper = $('.gallery-grid-item-wrap')
    var horizontalOrder = true

    if (wrapper.hasClass('std-creative-grid')) {
        horizontalOrder = false
    }

    var GalleryGridWrap = $('.gallery-grid-item-wrap').imagesLoaded(function () {
        GalleryGridWrap.masonry({
            itemSelector: '.gallery-grid-item',
            columnWidth: '.gallery-grid-item',
            transitionDuration: '0.65s',
            initLayout: true,
            originTop: true,
            horizontalOrder: horizontalOrder,
        })
    })
    $(window).on('resize', function () {
        GalleryGridWrap.masonry('bindResize')
    })

    var GalleryMasonryWrap = $('.gallery-masonry-item-wrap').imagesLoaded(function () {
        GalleryMasonryWrap.masonry({
            itemSelector: '.gallery-masonry-item',
            columnWidth: '.gallery-masonry-item',
            transitionDuration: '0.65s',
            initLayout: true,
            originTop: true,
            horizontalOrder: false,
        })
    })
    $(window).on('resize', function () {
        GalleryGridWrap.masonry('bindResize')
    })

    if (!wrapper.hasClass('std-creative-grid')) {
        $('.gallery-item').on('mouseover', function () {
            $(this).toggleClass('on-hover-item')
            $('.gallery-item:not(.on-hover-item)').css({ 'opacity': '0.5' })
        })
        $('.gallery-item').on('mouseleave', function () {
            $(this).removeClass('on-hover-item')
            $('.gallery-item').css({ 'opacity': '1' })
        })
    }

    var galleryItem = ''

    if ($('.gallery-masonry-item-wrap.gallery-masonry').length > 0) {
        galleryItem = '.gallery-masonry-item-wrap.gallery-masonry'
    } else {
        galleryItem = '.gallery-grid-item-wrap.gallery-grid'
    }

    $(`${galleryItem}`).lightGallery({
        thumbnail: false
    })

    //carousel album

    var carouselWrap = $('.carousel-block')
    var space = 25;
    var perView = 2
    var loop = !carouselWrap.hasClass('gallery-carousel-two') ? false : true

    !carouselWrap.hasClass('gallery-carousel-block') ? space : space = 5
    !carouselWrap.hasClass('gallery-carousel-two') ? perView : perView = "auto"

    var swiper = new Swiper(".carousel-album", {
        spaceBetween: space,
        mousewheel: true,
        loop: loop,
        navigation: {
            nextEl: ".next-prev-btn",
            prevEl: ".slide-prev-btn",
        },
        scrollbar: {
            el: ".swiper-scrollbar"
        },
        allowTouchMove: true,
        calculateHeight: true,
        breakpoints: {
            640: {
                slidesPerView: 2
            },
            1024: {
                slidesPerView: 2
            },
            1200: {
                slidesPerView: perView
            }
        }
    });

    if (carouselWrap.hasClass('gallery-carousel-block')) {
        $('.launch-gallery-icon').on('click', function () {
            $('.swiper-wrapper').lightGallery({
                thumbnail: false
            })
        })
    }

    //gallery animate
    var animatePage = $('.animate-scroll-block')

    if (animatePage.hasClass('animate-one')) {
        $('.animate-item-wrap').lightGallery({
            thumbnail: false
        })
    }

    $('.lightgallery-parent').lightGallery({
        thumbnail: false
    })

    //Archive page & Blog page
    var BlogLoopWrap = $('.blog-loop-wrap').imagesLoaded(function () {
        BlogLoopWrap.masonry({
            itemSelector: '.blog-card',
            columnWidth: '.blog-card',
            transitionDuration: '0.65s',
            initLayout: true,
            originTop: true,
            horizontalOrder: false,
        })
    })
    $(window).on('resize', function () {
        GalleryGridWrap.masonry('bindResize')
    })
})