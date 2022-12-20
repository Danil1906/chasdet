$(document).ready(function () {


// Анимация выезда меню бургер по нажатию

        $('.burger').on('click', function (el) {
            let burger_block_width = $('.category_dynamic_block').outerWidth()
            if ($('.category_dynamic_block').css('left') != '0px') {
                $('.category_dynamic_block').animate({
                    'left': '0px'
                })
                $('.burger-muted-background').addClass('muted-background-burger')
            } else {
                $('.category_dynamic_block').animate({
                    'left': `-${burger_block_width}px`
                });
                $('.burger-muted-background').removeClass('muted-background-burger')
            }
        });


        // Проверка куки для блока о предупреждения о сборе куки
        function checkCookies() {
            let cookieDate = localStorage.getItem('cookieDate');
            let cookieNotification = $('.cookie-notification__box')
            let cookieBtn = $('.cookie-notification__cookie-acceptbtn');

            // Если записи про кукисы нет или она просрочена на 1 год, то показываем информацию про кукисы
            if (!cookieDate || (+cookieDate + 31536000000) < Date.now()) {
                $(cookieNotification).css('display', 'block')
            }

            // При клике на кнопку, в локальное хранилище записывается текущая дата в системе UNIX
            $(cookieBtn).on('click', function (e) {
                e.preventDefault()
                console.log('Произошло нажатие')
                localStorage.setItem('cookieDate', Date.now());
                $(cookieNotification).css('display', 'none')
                console.log('Все отработало')
            })
        }

        checkCookies();


        // Раскрытие списка вопросов на страничке вопросов (FAQ)

        $('.faq__list-wrapper-question').on('click', function () {
            $($(this).siblings('.faq__list-wrapper-answer')).slideToggle();
            $(this).find('.wrapper-question__text').toggleClass('droped__answer')
        });

        // Позиционирование блока подверждения заказа по центру на странице оформления заказа
        OrderPopupPosition()

        function OrderPopupPosition() {
            if (document.location.href.indexOf('order') > 0) {
                let widthWindowPopup = Number($('.final-action__popup__inner').css('width').slice(0, -2))
                let posLeftPopup = window.innerWidth / 2 - widthWindowPopup / 2
                let bodyHeight = $('body').css('height')

                $('.final-action__popup-background').css('height', bodyHeight);
                $('.final-action__popup__inner').css({
                    left: posLeftPopup
                })
            }
        }

        $(window).resize(function () {
            OrderPopupPosition()
        });


        // Слайдер на главной
        $('.banner-section__slider').slick({
            slidesToShow: 1,
            slidesToScroll: 1,
            autoplay: true,
            autoplaySpeed: 2500,
            infinite: true,
            dots: true,
            nextArrow: `<button class="slider-arrow slider-arrow__next"><img src="static/image/svg/slider-arrow-rigth.svg" alt=""></button>\n`,
            prevArrow: '<button class="slider-arrow slider-arrow__prev"><img src="static/image/svg/slider-arrow-left.svg" alt=""></button>\n',
        });


        $(document).on('click touchstart', function (e) {
            var div = $('.category_dynamic_block')
            var div_css_left = div.css('left')
            if (!div.is(e.target) && div_css_left == '0px' && $('.pc-header').is(':visible') || $('.mobile-burger-close > img').is(e.target)) {

                $('.category_dynamic_block').animate({
                    'left': '-100%'
                });
                $('.burger-muted-background').removeClass('muted-background-burger')
            }
            ;
        });

// Отслеживания события наведения курсора на категории в бургере
        let burg = document.querySelectorAll('.li_for_root_leaf');

        burg.forEach(function (el) {
            el.addEventListener('mouseover', function () {
                let xy = $(this).position()
                $(this).find('.children').attr("style", "display: block")
                $(this).find('.children').css("top", xy['top'] - 20 + 'px');

            })

            el.addEventListener('mouseout', function () {
                $(this).find('.children').attr("style", "display: none")
            })

            $(el).on('touchstart', function () {
                if ($(this).find('.children').css('display') == 'none') {
                    $(this).find('.children').slideToggle('fast')
                } else {
                    $(this).find('.children').slideToggle('fast')
                }
                ;
            });

        });


// Transferring data from the form to the cart
//     Processing block of the add product page
        let product_cart_div = document.querySelectorAll('.prod-card-div')
        product_cart_div.forEach(function (el) {
            let hidden_quantity_in_cart = $(el).find('#quantity-from-cart')[0]
            let pc_and_mobile_variable_quantity = el.querySelectorAll('.variable-quantity')

            let variable_quantity_span = $(el).find('.variable-quantity')[0]
            let available_quantity = Number($(variable_quantity_span).text())
            let quantity_input = $(el).find('.quantity-input')

            let how_much_can_input = available_quantity - Number($(hidden_quantity_in_cart).text())

            let quantityArrowMinus = $(el).find(" a.quantity-arrow-minus");
            let quantityArrowPlus = $(el).find(".quantity-arrow-plus");
            let form_qu = $(el).find('#basket-form')

            if (how_much_can_input > 0) {
                $(quantity_input).val(1)
            } else {
                $(quantity_input).val(0)
            }

            $(pc_and_mobile_variable_quantity[0]).text(how_much_can_input)
            $(pc_and_mobile_variable_quantity[1]).text(how_much_can_input)

            $(quantity_input).attr('max', how_much_can_input)

            $(quantity_input).bind('input', function () {
                $(pc_and_mobile_variable_quantity[0]).text(how_much_can_input - $(this).val())
                $(pc_and_mobile_variable_quantity[1]).text(how_much_can_input - $(this).val())
            });

            $(quantityArrowMinus).on('click', function () {
                let vall = Number($(quantity_input).val())
                if (vall > 1) {
                    $(quantity_input).trigger('input', $(quantity_input).val(vall - 1))
                }
            });

            $(quantityArrowPlus).on('click', function () {

                let vall = Number($(quantity_input).val())
                if (vall < Number(available_quantity)) {
                    $(quantity_input).trigger('input', $(quantity_input).val(vall + 1))
                }
            });

            $(form_qu).submit(function (event) {
                event.preventDefault();
                const friendForm = $(this);
                const posting = $.post(friendForm.attr('action'), friendForm.serialize());
                posting.done(function (data) {
                    let number_items = data['count']
                    let count_btns = document.querySelectorAll('#count-items')
                    count_btns.forEach(function (el) {
                        $(el).text(number_items)
                    });
                    how_much_can_input = Number($(variable_quantity_span).text())
                    available_quantity = Number($(variable_quantity_span).text())
                    $(quantity_input).attr('max', how_much_can_input)
                    if (how_much_can_input > 0) {
                        $(quantity_input).val(1)
                    } else {
                        $(quantity_input).val(0)
                    }
                });
            });
        });

        // Обработка инпута количество товаров на страничке товаров (стекла)
        let all_product_list__item = document.querySelectorAll('.product-list__item')
        all_product_list__item.forEach(function (el) {
            let hidden_quantity_in_cart = $(el).find('#quantity-from-cart')[0]
            let variable_quantity_p = el.querySelectorAll('.variable-quantity')

            let variable_quantity_span = $(el).find('.variable-quantity')[0]
            let available_quantity = Number($(variable_quantity_span).text())
            let quantity_input = $(el).find('.quantity-input')

            let how_much_can_input = available_quantity - Number($(hidden_quantity_in_cart).text())

            let form_qu = $(el).find('#basket-form-glass')

            if (how_much_can_input > 0) {
                $(quantity_input).val(1)
            } else {
                $(quantity_input).val(0)
            }

            $(variable_quantity_p[0]).text(how_much_can_input)
            $(variable_quantity_p[1]).text(how_much_can_input)

            $(quantity_input).bind('input', function () {
                $(variable_quantity_p[0]).text(how_much_can_input - $(this).val())
                $(variable_quantity_p[1]).text(how_much_can_input - $(this).val())
            });

            $(quantity_input).attr('max', how_much_can_input)

            $(form_qu).submit(function (event) {
                event.preventDefault();
                const friendForm = $(this);
                const posting = $.post(friendForm.attr('action'), friendForm.serialize());
                posting.done(function (data) {
                    let number_items = data['count']
                    let count_btns = document.querySelectorAll('#count-items')
                    count_btns.forEach(function (el) {
                        $(el).text(number_items)
                    });
                    how_much_can_input = Number($(variable_quantity_span).text())
                    available_quantity = Number($(variable_quantity_span).text())
                    $(quantity_input).attr('max', how_much_can_input)
                    if (how_much_can_input > 0) {
                        $(quantity_input).val(1)
                    } else {
                        $(quantity_input).val(0)
                    }
                });
            });
        })


        // Place an order from the cart page using a promo code
        let ordering_div = $('#finel-price')
        let ordering_btn = $(ordering_div).find('#an_order_btn')[0]
        const ordering_form = $(ordering_div).find('form')
        $(ordering_btn).on('click', function (el) {
            // el.preventDefault()
            const posting = $.post($(ordering_btn).attr('href'), ordering_form.serialize());
            posting.done(function (data) {
                console.log('Готово')
            })
        });


        // delete from cart
        let all_items_carts = document.querySelectorAll('#item-cart-in-cart')

        all_items_carts.forEach(function (el) {
            let btn = el.querySelector('.remove-item-cart')
            btn.addEventListener('click', function (event) {
                event.preventDefault();
                let url = $(this).attr('href')
                $.ajax({
                    url: url,
                    method: 'get',
                    dataType: 'json',
                    success: function (data) {
                        let number_items = data['count']
                        let total_price = data['total_price']
                        let count_btns = document.querySelectorAll('#count-items')
                        count_btns.forEach(function (el) {
                            $(el).text(number_items)
                        });
                        let str_total = $('#finel-price').find('.total-price').text().split(' ')

                        let change_total = str_total[0] + ' ' + total_price
                        $('#finel-price').find('.total-price').text(change_total)

                        $(el).hide('fast', function () {
                            $(this).remove();
                        });
                    }
                })
            });
        });

        // login button
        function clickBtnSingIn(el) {
            let str_height = $(window).height()
            let background_muted = $('.muted-background-login-block')
            $('.login_block').css('top', (str_height / 2) / 2)
            $('.login_block').css('display', 'block')
            let all_login_blocks = document.querySelectorAll('.login_block')


            $(background_muted).css('height', str_height)
            $(background_muted).css('display', 'block')

            $('.login_block').hide()
            $(background_muted).hide()

            $('.login_block').show('fast')
            $(background_muted).show('fast')

        };

        $('#btn-in').on('click', function (el) {
            el.preventDefault()
            clickBtnSingIn(el)
        })


        $('#btn-in-mobile').on('click', function (el) {
            el.preventDefault()
            clickBtnSingIn(el)
        })

        $(document).on('click', function (e) {
            let background_muted = $('.muted-background-login-block')
            let div = $('.login_block')
            let div_btn_log = $('#btn-in')
            let mobile_btn = $('#btn-in-mobile')


            if ($(div).css('display') != 'none'
                && div.has(e.target).length === 0
                && div_btn_log.has(e.target).length === 0
                && mobile_btn.has(e.target).length === 0) {
                $('.login_block').hide('fast')
                $(background_muted).hide('fast')
            }

        });


        // Site login processing
        $('.form-btn-submit').on('click touchstart', function (el) {
            let form = document.querySelectorAll('#login-form-main')
            form.forEach(function (el) {
                if ($(el).is(':visible')) {
                    form = el
                }
            });
            $(form).submit(function (event) {
                event.preventDefault();
                const logForm = $(this);
                const posting = $.post(logForm.attr('action'), logForm.serialize());
                posting.done(function (data) {
                    let background_muted = $('.muted-background-login-block')

                    $(background_muted).hide('fast')
                    let inputs = document.querySelector('.login_block').querySelectorAll('input.form-control')
                    inputs.forEach(function (el) {
                        $(el).val('')
                    });

                    $('.login_block').attr('hidden', 'hidden')
                    location.reload()
                });
                posting.fail(function (data) {
                    $('.it-if-error').css('display', 'block')
                    console.log('Что то не так')
                    if (data['reload']) {
                        location.reload()
                    }
                });
            });
        });

        // if ($('#checkMe').is(':checked')) {
        //     console.log('Выбрано')
        // }

        // Обработка запроса уведомления о наличии товара.
        let all_form_notify = document.querySelectorAll('#basket-form-notify')
        all_form_notify.forEach(function (el) {
            let form = $(el)[0]
            let action = $(form).attr('action')
            let this_btn = $(form).find('#menotify')

            $(el).on('submit', function (event) {
                event.preventDefault()
                const post_it = $.post(action, $(form).serialize());

                post_it.done(function (data) {
                    if (data['status'] === 'noauth') {
                        clickBtnSingIn()
                    } else if (data['status'] === 'auth') {
                        $(this_btn).attr('disabled', '')
                        $(this_btn).val('✓')
                    }
                });
                post_it.fail(function (data) {
                    console.log(data)
                })
            })
        })

        // Remove all items from the cart
        $('#main-check-cart').on('click', function (el) {
            let all_cheks = document.querySelectorAll('#check-in-card')
            if ($(this).is(':checked')) {
                all_cheks.forEach(function (check) {
                    if ($(check).is(':checked')) {
                    } else {
                        $(check).trigger('click')
                    }
                });
            } else {
                all_cheks.forEach(function (el) {
                    $(el).trigger('click');
                    if ($(el).is(':checked')) {
                        $(el).trigger('click');
                    }
                });
            }
        });


        $('#del-all-selected').on('click', function (event) {
            event.preventDefault()
            let buttons_id = ''
            let url = $(this).attr('href')

            let checked_form = document.querySelectorAll('#check-in-card:checked')
            if (checked_form.length > 0) {

                checked_form.forEach(function (el) {
                    let form = $(el).parents('#item-cart-in-cart')[0];
                    let some = $(form).find('.remove-item-cart')

                    some = $(some).attr('href')
                    some = some.split('/')
                    some = some[some.length - 2]
                    some = String(some)

                    buttons_id += some
                    buttons_id += '-'
                });
                url = url.substr(0, url.length - 3) + buttons_id
                url = url.substr(0, url.length - 1)
                $.ajax({
                    url: url,
                    method: 'get',
                    dataType: 'json',
                    success: function (data) {
                        console.log('Успешное удаление')

                        if ($('#main-check-cart').is(':checked')) {
                            console.log('Почему то сработало')
                            $('#main-check-cart').trigger('click')
                        }

                        let number_items = data['count']
                        let total_price = data['total_price']
                        let count_btns = document.querySelectorAll('#count-items')
                        count_btns.forEach(function (el) {
                            $(el).text(number_items)
                        });
                        let str_total = $('#finel-price').find('.total-price').text().split(' ')

                        let change_total = str_total[0] + ' ' + total_price
                        $('#finel-price').find('.total-price').text(change_total)

                        checked_form.forEach(function (el) {
                            let form = $(el).parents('#item-cart-in-cart')[0];
                            $(form).hide('fast', function () {
                                $(this).remove();
                            });
                        });

                    }
                });
            }
        });

        // changing the quantity of items in the cart
        let changer = document.querySelectorAll('#item-cart-in-cart')
        let show_total_price = 0.0

        changer.forEach(function (el) {
            let form_div = $(el).find('#quantity-update-form')[0]
            let checkbox = $(form_div).find('form').find('#quantity-update')
            let number_int = $(form_div).find('.quantity-input')[0]
            let quantity = $(el).find('form').find('p[hidden]')[0]
            // Ниже это блок с отображение инпута и колво
            let residue_div = $(form_div).find('#quantity-for-clients')[0]
            let hidden_quantity = $(residue_div).find('p[hidden]')[0]
            let final_residue = $(residue_div).find('span')[0]
            let total_price = $($('.total-price')[0]).text()
            total_price = total_price.split(' ')
            let first_total_price_part = total_price[0]
            let old_color = $(final_residue).css('color')

            let total_item_price_on_page = $(el).find('.item_total_price').find('span')

            let price_per_unit = $($(form_div).find('.price-per-unit')[0]).text()

            let quantityArrowMinus = $(el).find(" a.quantity-arrow-minus");
            let quantityArrowPlus = $(el).find(".quantity-arrow-plus");


            price_per_unit = Number(price_per_unit.replace(',', '.'))

            $(final_residue).text($(hidden_quantity).text() - $(quantity).text())

            show_total_price += price_per_unit * Number($(number_int).val())

            if (Number($(quantity).text()) > Number($(hidden_quantity).text())) {
                $(residue_div).text('Указано больше, чем доступно на данный момент. Всего доступно ' + $(hidden_quantity).text())
                $(residue_div).css('color', 'red')
            }

            $(number_int).val($(quantity).text())

            let total_item_price = Number((Number($(number_int).val()) * price_per_unit).toFixed(2))

            show_total_price += total_item_price

            $(number_int).keydown(function (e) {
                if (e.keyCode === 13) {
                    e.preventDefault()
                }
            });

            $(number_int).attr('max', $(hidden_quantity).text())

            $(quantityArrowMinus).on('click', function () {
                let vall = Number($(number_int).val())
                if (vall > 1) {
                    $(number_int).trigger('input', $(number_int).val(vall - 1))
                }
            });

            $(quantityArrowPlus).on('click', function () {

                let vall = Number($(number_int).val())
                if (vall < Number($(hidden_quantity).text())) {
                    $(number_int).trigger('input', $(number_int).val(vall + 1))
                }
            });


            $(number_int).bind('input', function () {

                if (Number($(this).val()) <= Number($(hidden_quantity).text())) {

                    show_total_price -= total_item_price
                    total_item_price = Number((Number($(this).val()) * price_per_unit).toFixed(2))
                    show_total_price += total_item_price
                    show_total_price = show_total_price.toFixed(2)
                    $(total_item_price_on_page).text(String(total_item_price))

                    $('.total-price').text(first_total_price_part + ' ' + show_total_price.replace('.', ','))
                    $()


                    $(residue_div).text('еще доступно: ' + ($(hidden_quantity).text() - $(number_int).val()))
                    $(residue_div).css('color', old_color)
                    $(checkbox).val('True')
                    setTimeout(function () {
                        let form = $(el).find('form')
                        let action = $(form).attr('action')
                        const posting = $.post(action, $(form).serialize());
                        posting.done(function () {

                        });
                        posting.fail(function () {
                        });
                    }, 500);
                } else {
                    $(residue_div).text('Вы пытайтесь ввести больше чем доступно. Всего доступно ' + $(hidden_quantity).text())
                    $(residue_div).css('color', 'red')

                    setTimeout(function () {
                        $(final_residue).attr('style', 'color:' + old_color)
                    }, 2500)
                }
            });
        });


        // Звездный рейтинг на товаре

        $("#rateYo").rateYo({
            readOnly: true,
            ratedFill: "#F28D2A"
        });

        $("#rateYo_user").rateYo({
            ratedFill: "#007DBA",
            fullStar: true
        });

// Получаю рейтин
        $('.prod-card__review_button').on('click', function (e) {
            e.preventDefault()
            let rateYo = $("#rateYo_user").rateYo();
            let rating = rateYo.rateYo("rating");
            console.log(rating)
            if (rating == 0) {
                $('.rate-star__input-hidden').val(5)
            } else {
                $('.rate-star__input-hidden').val(rating)
            }

            let form = $('.prod-card__review_form')
            let action = $(form).attr('action')
            const posting = $.post(action, $(form).serialize());
            posting.done(function (data) {
                document.location.reload();
            });
            posting.fail(function (data) {
                document.location.reload();
            });
        });


        $('.prod-card__btn_activation').on('click', function (e) {
            $('.prod-card__review_formbox').slideToggle()
        })

        // Delivery page unit
        if (window.location.pathname.includes('order')) {

            let block = $('#changeable-js-block')[0]
            let block_input = $('#index-input')[0]
            let standart_style_input = $(block_input).css('border')
            let label_input = $('#changeable-js-block').find('label')[0]
            let standart_label_input = $(label_input).text()
            let btn_block = $('#input-delivery-btn')[0]
            let second_step = $('#s-changeable-js-block')
            $(second_step).hide()


            $(block_input).on('input', function (el) {

                if ($(this).val().length > 6) {
                    $(this).css('border', '1px solid red')
                    $(label_input).text('Индекс должен состоять из 6 цифр')
                    $(label_input).css('color', 'red')

                } else {
                    $(this).css('border', standart_style_input)
                    $(label_input).text(standart_label_input)
                    $(label_input).css('color', 'black')
                }

                if ($(this).val().length == 6) {
                    $(btn_block).attr('style', 'display: block')
                } else {
                    $(btn_block).attr('style', 'display: none')
                }
            });

            function yaMapCaller(data, cdek, phone, email, full_cdek) {

                let zoom = 12
                if (cdek['features'].length > 100) {
                    console.log('Изменение стартового масштаба карты в связи с большим пакем объектов')
                    zoom = 9
                }

                ymaps.ready(init);

                function init() {
                    // Creating the map.
                    let inputSearch = new ymaps.control.SearchControl({
                        options: {
                            // Пусть элемент управления будет
                            // в виде поисковой строки.
                            size: 'small',
                            // Включим возможность искать
                            // не только топонимы, но и организации.
                            provider: 'yandex#search'
                        }
                    })

                    var myMap = new ymaps.Map("map", {
                            center: [cdek['features'][0]['geometry']['coordinates'][0],
                                cdek['features'][0]['geometry']['coordinates'][1]],

                            controls: ['geolocationControl', 'zoomControl', inputSearch],
                            zoom: zoom
                        }, {
                            searchControlProvider: 'yandex#search'
                        }),
                        objectManager = new ymaps.ObjectManager({
                            // Чтобы метки начали кластеризоваться, выставляем опцию.
                            clusterize: true,
                            // ObjectManager принимает те же опции, что и кластеризатор.
                            gridSize: 32,
                            clusterDisableClickZoom: true,
                            clusterOpenBalloonOnClick: false
                        });

                    objectManager.objects.options.set('preset', 'islands#greenDotIcon');
                    objectManager.clusters.options.set('preset', 'islands#greenClusterIcons');
                    myMap.geoObjects.add(objectManager);

                    objectManager.add(cdek);

                    // обработка события нажатия на конкретную метку на карте
                    function onObjectEvent(e) {
                        var objectId = e.get('objectId');
                        if (e.get('type') == 'click') {

                            let map_width = $('#map').css('width')
                            let map_height = $('#map').css('height')

                            if ($("#map-block").length) {
                                $("#map-block").remove();
                            }

                            // add a block to confirm the selected address
                            let offset = $('#map').offset()
                            let block = $('<div class="alert-message m-3 p-2" id="map-block" style="position: absolute; ' +
                                'background: white; border: 1px solid silver">Хотите выбрать этот пункт? <br> ' +
                                '<div class="d-flex justify-content-around my-2">' +
                                '<a href="#" class="btn btn-danger btn-sm mx-2" id="map-yes">Да</a>' +
                                '<a href="#" class="btn btn-secondary btn-sm mx-2" id="map-no">Нет, другой</a></div></div>')

                            let input_block = $('<div class="alert-message m-3 p-2 container align-items-center ' +
                                'rounded-bottom" id="map-input" ' +
                                'style="background: white">' +
                                '<div class="d-flex w-100 flex-wrap justify-content-center mt-2">' +
                                '<p class="w-100 text-center"><small class="cdek-form__info">Заполните данные для доставки</small></p>' +
                                '<p class="w-100 text-center error-info-block" style="color: red"></p>' +
                                '<input class="form-control w-50 my-1 mx-3 phone-input phone-input__cdek-map"  required type="phone" placeholder="Телефон.."><br>' +
                                '<input class="form-control my-1 mx-3 w-50 f-name" type="text" required  placeholder="Ф.И.О."><br>' +
                                '<input class="form-control my-1 mx-3 w-50 f-email" type="text" required  placeholder="Email"><br>\'' +
                                '</div>' +
                                '<div class="d-flex flex-wrap justify-content-center">' +
                                '<button href="#" class="btn btn-warning btn-sm mt-2 mb-1 call-ajax">Подтвердить</button><br>' +
                                '<a href="#" class="text-muted w-100 text-center " style="text-decoration: none;">' +
                                '<small class="cancel-btn">Отмена</small></a>' +
                                '</div>' +
                                '</div>')

                            $('#map').append(block)
                            $('#map-block').css('z-index', '3500')
                            $(block).offset({top: offset.top, left: offset.left})

                            // Отслеживание нажатии клавиши да в блоке подверждения выбора на карте сдек и подставление данных в форму
                            $('#map-yes').on('click', function () {
                                $(block).remove();
                                $('#map').append(input_block);
                                $(input_block).offset({top: offset.top, left: offset.left});
                                $(input_block).css('width', map_width);
                                if (phone != null) {
                                    $('.phone-input').val(phone)
                                    $('.f-email').val(email)
                                }
                                $('.cancel-btn').on('click', function () {
                                    $(input_block).remove()
                                });


                                // Валидация инпутов в форме сдека
                                // инпут телефона
                                $('.phone-input__cdek-map').bind('focusout', function (e) {
                                    let phone_input = $(this).val()
                                    let phone_input_val = phone_input.split(' ').join('').split('-').join('')

                                    let regex = /^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$/;
                                    // дальше идет проверка на соответствие выражению
                                    if (!regex.test(phone_input_val)) {
                                        // disabled
                                        $('.call-ajax').attr('disabled', '')
                                        $(this).addClass('input__error')
                                        $('.cdek-form__info').text('Формат ввода +7 910 000 0000').css('color', 'red')

                                    } else {
                                        $('.call-ajax').removeAttr('disabled')
                                        $(this).removeClass('input__error')
                                        $('.cdek-form__info').text('Номер телефона:').css('color', 'black')
                                        if (phone_input_val.length === 11) {
                                            if (Number(phone_input_val[0] === '7')) {
                                                phone_input_val = '+' + phone_input_val
                                                $(this).val(phone_input_val)

                                            } else if (Number(phone_input_val[0] === '8')) {
                                                phone_input_val = '+' + '7' + phone_input_val.slice(1)
                                                $(this).val(phone_input_val)
                                            }
                                        }
                                    }
                                });

                                // инпут ФИО
                                $('.f-name').bind('focusout', function (e) {
                                    let input_fullname = $(this).val()
                                    for (let i = 0; i < input_fullname.length; i++) {
                                        let letter = input_fullname[i]
                                        if (/[a-zA-Z]/.test(letter) || !isNaN(letter)) {
                                            // тут есть англ буквы
                                            $('.call-ajax').attr('disabled', '')
                                            $(this).addClass('input__error')
                                            $('.cdek-form__info').text('В Ф.И.О. не должно быть латиницы и числовых значений, только кирилицца (русский алфавит)').css('color', 'red')
                                        } else {
                                            $('.call-ajax').removeAttr('disabled')
                                            $(this).removeClass('input__error')
                                            $('.cdek-form__info').text('Ф.И.О.').css('color', 'black')
                                        }
                                    }
                                })

                                $('.call-ajax').on('click', function () {
                                    if ($('.f-name').val() && $('.phone-input').val() && $('.f-email').val()) {
                                        $('#full-name-delivery').val($('.f-name').val())
                                        $('#phone-delivery').val($('.phone-input').val())
                                        $('#email-delivery').val($('.f-email').val())
                                        $('#street-delivery').val(full_cdek[objectId]['address'])

                                        const order_form = $('#order-delivery-main-form')[0]
                                        const action = $(order_form).attr('action')

                                        // Отправление формы на сервер
                                        confirmDataAndPost(action, order_form)

                                    } else {
                                        $('.error-info-block').append('<small>Для того что бы продлолжить, ' +
                                            'необходимо заполнить все поля</small>')
                                    }
                                });


                            });
                            // Отслеживание клавиши нет
                            $('#map-no').on('click', function () {
                                $(block).remove();
                            });

                            $(window).on('resize', function () {
                                let offset = $('#map').offset()
                                if ($(block).length) {
                                    $(block).offset({top: offset.top, left: offset.left})
                                }

                                if ($(input_block).length) {
                                    $(input_block).offset({top: offset.top, left: offset.left})
                                }
                            });
                        } else {
                            objectManager.objects.setObjectOptions(objectId, {
                                preset: 'islands#greenIcon'
                            });
                        }
                    }

                    objectManager.objects.events.add(['click'], onObjectEvent);
                }
            };


            // Валидация инпута номера в форме почты РФ
            $('#phone-delivery').bind('focusout', function (e) {
                let phone_input = $(this).val()
                let phone_input_val = phone_input.split(' ').join('').split('-').join('')

                let regex = /^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$/;
// дальше идет проверка на соответствие выражению
                if (!regex.test(phone_input_val)) {
                    // disabled
                    $('#main-form-btn').attr('disabled', '')
                    $(this).addClass('input__error')
                    $('label[for="phone-delivery"]').text('Формат ввода +7 910 000 0000').css('color', 'red')

                } else {
                    $('#main-form-btn').removeAttr('disabled')
                    $(this).removeClass('input__error')

                    $('label[for="phone-delivery"]').text('Номер телефона:').css('color', 'black')
                    if (phone_input_val.length === 11) {
                        if (Number(phone_input_val[0] === '7')) {
                            phone_input_val = '+' + phone_input_val
                            $(this).val(phone_input_val)

                        } else if (Number(phone_input_val[0] === '8')) {
                            phone_input_val = '+' + '7' + phone_input_val.slice(1)
                            $(this).val(phone_input_val)
                        }
                    }
                }
            });

            // Валидация инпута ФИО в форме почты рф
            $('#full-name-delivery').bind('focusout', function (e) {
                let input_fullname = $(this).val()
                for (let i = 0; i < input_fullname.length; i++) {
                    let letter = input_fullname[i]
                    if (/[a-zA-Z]/.test(letter) || !isNaN(letter)) {
                        // тут есть англ буквы
                        $('#main-form-btn').attr('disabled', '')
                        $(this).addClass('input__error')
                        $('label[for="full-name-delivery"]').text('В Ф.И.О. не должно быть латиницы и числовых значений, только кирилицца (русский алфавит)').css('color', 'red')
                    } else {
                        $('#main-form-btn').removeAttr('disabled')
                        $(this).removeClass('input__error')
                        $('label[for="full-name-delivery"]').text('Ф.И.О.').css('color', 'black')
                    }
                }
            })

            // Вызов попап с подтверждением информации и отправкой на сервер
            function confirmDataAndPost(action, order_form) {
                // Появление блока подтверждения заказа
                $('.final-action__popup').show();

                let delyvAdress = $('#region-delivery').val() + ' '
                    + $('#city-delivery').val() + ' '
                    + $('#street-delivery').val()


                $('.final-action__popup-deliveryname .popup-delivery__span-userdata').text($('#full-name-delivery').val())
                $('.final-action__popup-deliveryaddress .popup-delivery__span-userdata').text(delyvAdress)
                $('.final-action__popup-deliverymail .popup-delivery__span-userdata').text($('#email-delivery').val())
                $('.final-action__popup-deliveryphone .popup-delivery__span-userdata').text($('#phone-delivery').val())
                if ($('.discount__user-info').length) {
                    let discount_per = $('.discount__user-info span').text()
                    let total_sum_with_dis = $('.discount__price-discount span.sum-total__target').text().split(' ')[0]
                    total_sum_with_dis = Number(total_sum_with_dis.split(',')[0])
                    let coast_delivery = $('#delivery_price .delivery_price-target').text().split(' ')[1]
                    coast_delivery = Number(coast_delivery.split(',')[0])
                    let final_sum = total_sum_with_dis + coast_delivery

                    $('.popup-delivery__span-title span').text(final_sum)
                    $('.popup-delivery__span-discount').css('display', 'block')
                    $('.popup-delivery__span-discount span').text(discount_per)
                } else {

                    let total_sum_nodis = ($('.discount__price-nodiscount .sum-total__target').text().split(' ')[0])
                    total_sum_nodis = Number(total_sum_nodis.split(',')[0])
                    let coast_delivery = $('#delivery_price .delivery_price-target').text().split(' ')[1]
                    coast_delivery = Number(coast_delivery.split(',')[0])
                    let final_sum = total_sum_nodis + coast_delivery
                    $('.popup-delivery__span-title span').text(final_sum)
                }

                $('.final-action__form-btn').on('click', function (event) {
                    event.preventDefault()

                    $('.final-action__form').css('display', 'none')
                    $('.windows8').css('display', 'block')

                    const post_it = $.post(action, $(order_form).serialize());
                    post_it.done(function (data) {
                        console.log('Формочка успешно ушла')
                        window.location.href = data['redirect'];
                    });
                    post_it.fail(function (data) {
                        console.log('Ошибка где то кроется')
                        document.location.reload();
                    })
                })
            }

            $('.final-action__form-btncansel').on('click', function (e) {
                e.preventDefault()

                $('.final-action__popup').hide()
            });


            $('.final-action__popup-background').on('click', function (e) {
                $('.final-action__popup').hide()
            })


            //     ОБработка клика по кнопкам готового адреса (если пользователь ранее покупал, то на страничке, перед формой
            // ввода индекса будут предложены 2 или 1 клавиша, с сдек и\или почта в зависимости какие данные он ранее вводил)
            $('.auto-sender__bnt-cdek, .auto-sender__bnt-pochta').on('click', function (e) {
                e.preventDefault()

                const order_form = 'none'
                const action = $(this).attr('href')

                const post_it = $.get(action, $(order_form).serialize());
                post_it.done(function (data) {
                    let fio = data['fio']
                    let phone = data['phone']
                    let email = data['email']
                    let address = data['address'].split('-')
                    let address_popup = address.join(' ')
                    let region = address[0]
                    let city = address[1]
                    let street = address[2]
                    let total_price = data['total_price']

                    $('.final-action__popup').show();

                    if (Number.isInteger(data['discount'])) {
                        let discount = data['discount']
                        $('.popup-delivery__span-discount').css('display', 'block')
                        $('.popup-delivery__span-discount span').text(discount + '%')
                    }


                    $('.final-action__popup-deliveryname .popup-delivery__span-userdata').text(fio)
                    $('.final-action__popup-deliveryaddress .popup-delivery__span-userdata').text(address_popup)
                    $('.final-action__popup-deliverymail .popup-delivery__span-userdata').text(email)
                    $('.final-action__popup-deliveryphone .popup-delivery__span-userdata').text(phone)
                    $('.popup-delivery__span-title span').text(' ' + total_price + ' руб')

                    let block = $('#changeable-js-block')[0]
                    let second_step = $('#s-changeable-js-block')

                    $(block).hide('fast')
                    $(second_step).show('slow')

                    $('#region-delivery').val(region)
                    $('#index-delivery').val('000000')
                    $('#city-delivery').val(city)
                    $('#street-delivery').val(street)
                    $('#full-name-delivery').val(fio)
                    $('#email-delivery').val(email)
                    $('#phone-delivery').val(phone)

                    // Заполнение скрытого инпута который передает серверу инфомацию о выбранной доставке
                    // Данные формируются из ссылки висящей на линках
                    let this_active_link = $(this)[0]['url'].split('/').slice(-2, -1)[0]
                    $('#delivery-name').val(this_active_link)

                    const main_form_order = $('#order-delivery-main-form')[0]
                    const main_form_action = $(main_form_order).attr('action')

                    $('.final-action__form-btn').on('click', function (event) {
                        event.preventDefault()

                        $('.final-action__form').css('display', 'none')
                        $('.windows8').css('display', 'block')

                        const post_it = $.post(main_form_action, $(main_form_order).serialize());

                        post_it.done(function (data) {
                            console.log('Формочка успешно ушла')
                            console.log(data)
                            window.location.href = data['redirect']
                        });
                        post_it.fail(function (data) {
                            console.log('Ошибка где то кроется')
                            console.log(data)
                            document.location.reload();
                        })
                    })
                });
                post_it.fail(function (data) {
                    console.log('Ошибка где то кроется')
                    console.log(data)
                })
            });

            $(btn_block).on('click', function (event) {
                event.preventDefault()
                const form = $(block).find('form')[0]
                let action = $(form).attr('action')
                const posting = $.post(action, $(form).serialize());
                posting.done(function (data) {
                    $(block).hide('fast')
                    $(second_step).show('slow')
                    let pochta = data['pochta']
                    let cdek = data['cdek']
                    let full_cdek = data['full_cdek']
                    let phone = null
                    let cdek_price = $('#cdek-price').text() + ' руб.'
                    let pochta_price = $('#pochta-price').text() + ' руб.'

                    // в случае если пользователь авторизован, автомато подхватит его номер из профиля
                    if ($('#take-phone').length) {
                        $('#phone-delivery').val($('#take-phone').text())
                        phone = $('#take-phone').text()
                    }

                    if ($('#take-email').length) {
                        $('#email-delivery').val($('#take-email').text())
                        email = $('#take-email').text()
                    }

                    if (pochta['city'] && !!full_cdek.length) {
                        // тут функционал при наличии данных и от сдек и от почты
                        $('#region-delivery').val(pochta['region'])
                        $('#city-delivery').val(pochta['city'])
                        $('#index-delivery').val(pochta['index'])

                        yaMapCaller(data, cdek, phone, email, full_cdek)

                        // cdek delivery block with display on the map

                    } else if (pochta['city']) {
                        // тут возврат сообщения что сдека нет
                        $('#radio-dek').remove()
                        $('#block-1').remove()
                        $('#radio-pochta').remove()
                        $('#block-2').fadeIn();
                        $('#region-delivery').val(pochta['region'])
                        $('#city-delivery').val(pochta['city'])
                        $('#index-delivery').val(pochta['index'])
                        $('#delivery-name').val(2)
                        $('#delivery_price').html('<small class="text-muted">+ стоимость доставки Почта России:' + '<span class="delivery_price-target"> ' + pochta_price + '</span></small>')
                        if (phone != null) {
                            $('#phone-delivery').val(phone)
                        }


                        console.log('Есть только почта')
                    } else if (!!full_cdek.length) {
                        // тут что то непонятное, скорее всего почта легла, просто автозаполнение нужно убрать
                        // оставить ручной или сделать автозаполнение из данных сдека
                        $('#region-delivery').val(full_cdek[0]['region'])
                        $('#city-delivery').val(full_cdek[0]['city'])
                        $('#index-delivery').val(full_cdek[0]['index'])

                        yaMapCaller(data, cdek, phone, full_cdek)
                        console.log('Есть только сдек')
                    } else {
                        // ну а тут или пользователь ввел не корректный индекс, или все полегло, просто
                        // вывести возможность указать ручками данные для любой службы
                        $('#radio-dek').remove()
                        $('#block-1').remove()
                        $('#radio-pochta').remove()
                        $('#block-2').fadeIn();
                        $('.label-in-pochta-block').remove()
                        if (phone != null) {
                            $('#phone-delivery').val(phone)
                        }

                        let new_info = $('<div>' +
                            '<p class=""><span style="color: red">Похоже на ошибку.</span> Возможно не правильно передан <b>индекс</b> или ' +
                            'ошибки на стороне сайта. Пожалуйства, обновите страницу и попробуйте еще раз, если ' +
                            'результат такой же, то на данный момент доступно только ручное указание данных для отправления..</p>' +
                            '<p><span class="badge rounded-pill bg-warning text-dark mt-3 me-2">1</span><span>Укажите спопоб отправки</span></div></p>' +
                            '<p>' +
                            '<label><input type="radio" name="radi" value="1" required>CDEK</label><br>\n' +
                            '<label><input type="radio" name="radi" value="2">Почта России</label><br>\n' +
                            '</p>' +
                            '<p><span class="badge rounded-pill bg-warning text-dark mt-3 me-2">2</span><span>Заполните форму</span></div></p>' +
                            '<p class="text-muted"><small>Если вы выбрали CDEK, то в поле "Улица" укажите желаемый пункт выдачи ' +
                            'в вашем городе, в случае выробора "Почта России" указывать следует ваш адрес</small></p>' +
                            '</div>')

                        $('#order-delivery-main-form').before(new_info)

                        $('input[name="radi"]').click(function () {
                            $('#delivery-name').val($(this).val())
                            if ($(this).val() == 2) {
                                $('#delivery_price').html('<small class="text-muted">+ стоимость доставки Почта России:' + '<span class="delivery_price-target"> ' + pochta_price + '</span></small>')

                            }

                            if ($(this).val() == 1) {
                                $('#delivery_price').html('<small class="text-muted">+ стоимость доставки Почта России:' + '<span class="delivery_price-target"> ' + cdek_price + '</span></small>')
                            }
                        });
                        console.log('Нет данных ни по сдеку ни по почте')
                    }

                });

                posting.fail(function (data) {
                    console.log('Что то не так')
                    console.log(data)
                    // Тут стоит прописать блок ручного ввода данных на тот случай если апишки не работают.
                });

            });


            // Отслеживание и обработка события отправки формы с "почта россии"
            // Единственное в условиях в блоке обработке клика при отправке индекса, есть ответвление
            // при котором от сервера не пришел ответ ни по почте, ни по сдеку, там формируются в форму
            // собственные радио бАтоны. тут отслеживается есть ли такие в форме и если да, выбраны ли те

            $('#main-form-btn').click(function (event) {
                event.preventDefault()
                const order_form = $('#order-delivery-main-form')[0]
                const action = $(order_form).attr('action')
                let inputs = $(order_form).find('input')
                let empty_inputs = []

                for (let i = 0; i < inputs.length; i++) {
                    if (!$(inputs[i]).val()) {
                        empty_inputs.push(inputs[i])
                    }
                }

                if (empty_inputs.length == 0) {
                    if ($('input[name="radi"]').length) {
                        if (!($('input[name="radi"]').is(':checked'))) {
                            event.preventDefault()
                            let rd = $('input[name="radi"]')[0]
                            let alert = $('<div class="alert alert-warning alert-dismissible fade show" role="alert">\n' +
                                '<strong>выберете способ доставки</strong>' +
                                '</div>')
                            $(rd).before(alert)
                            setTimeout(function () {
                                $(alert).remove()
                            }, 2000)
                            return
                        }
                    }

                    confirmDataAndPost(action, order_form)
                } else {
                    for (let i = 0; i < empty_inputs.length; i++) {
                        $(empty_inputs[i]).addClass('input__error')
                    }
                    empty_inputs = []
                }
            });

            $('input[name="radio"]').click(function () {
                let cdek_price = $('#cdek-price').text() + ' руб.'
                let pochta_price = $('#pochta-price').text() + ' руб.'
                let target = $('#block-' + $(this).val());

                $('#delivery-name').val($(this).val())

                if ($(this).val() == 2) {
                    $('#delivery_price').html('<small class="text-muted">+ стоимость доставки Почта России:' + '<span class="delivery_price-target"> ' + pochta_price + '</span></small>')
                }

                if ($(this).val() == 1) {
                    $('#delivery_price').html('<small class="text-muted">+ стоимость доставки Почта России:' + '<span class="delivery_price-target"> ' + cdek_price + '</span></small>')
                }

                $('.block-text-delivery').not(target).hide(0);
                target.fadeIn(500);
            });
        }

        // Клавиша наверх
        $('#button-up').click(function (el) {
            el.preventDefault()
            $('body,html').animate({
                scrollTop: 0
            }, 600);
            return false;
        });

        // Якортные ссылки
        $('a[href^="#"]').click(function (e) {
            e.preventDefault()
            let anchor = $(this).attr('href');
            $('html, body').animate({
                scrollTop: $(anchor).offset().top
            }, 600);
        });


        $('img.img-blue').each(function () {
            let $img = $(this);
            let imgClass = $img.attr('class');
            let imgURL = $img.attr('src');
            $.get(imgURL, function (data) {
                let $svg = $(data).find('svg');
                if (typeof imgClass !== 'undefined') {
                    $svg = $svg.attr('class', imgClass + ' replaced-svg');
                }
                $svg = $svg.removeAttr('xmlns:a');
                if (!$svg.attr('viewBox') && $svg.attr('height') && $svg.attr('width')) {
                    $svg.attr('viewBox', '0 0 ' + $svg.attr('height') + ' ' + $svg.attr('width'))
                }
                $img.replaceWith($svg);
            }, 'xml');
        });

        // Changes for mobile permissions

        $('.dots-mobile-header').on('click', function () {
            $('.dinamic-link-block-mobile').slideToggle()
        });

        let base_height = $(window).outerHeight()
        let doc = document.body
        $('.test-it').text(base_height)
        $(window).on('scroll', function (el) {
            if ($(window).outerHeight() > base_height) {
                $('.muted-background-login-block').css('height', $(window).outerHeight())
            }
        });

    }
);