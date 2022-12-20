

$(document).ready(function () {

// Анимация выезда меню бургер по нажатию

$('.burger_button').on('click', function(el) {
    let burger_block_width = $('.category_dynamic_block').outerWidth()
    if ( $('.category_dynamic_block').css('left') != '0px') {
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

// $(document).on('click', function (e) {
//     var div = $('.category_dynamic_block')
//     var div_css_left = div.css('left')
//     if (!div.is(e.target) && div_css_left == '0px' ) {
//         console.log(!div.is(e.target))
//
//         $('.category_dynamic_block').animate({
//         'left': '-100%'
//     });
//         $('.burger-muted-background').removeClass('muted-background-burger')
//     };
// });

$(document).on('click touchstart', function (e) {
    var div = $('.category_dynamic_block')
    var div_css_left = div.css('left')
    if (!div.is(e.target) && div_css_left == '0px' && $('.pc-header').is(':visible') || $('.mobile-burger-close > i').is(e.target)) {
        console.log(!div.is(e.target))

        $('.category_dynamic_block').animate({
        'left': '-100%'
    });
        $('.burger-muted-background').removeClass('muted-background-burger')
    };
});

// Отслеживания события наведения курсора на категории в бургере

let burg = document.querySelectorAll('.li_for_root_leaf');

burg.forEach(function (el) {
    el.addEventListener('mouseover', function () {
        let xy = $(this).position()
        $(this).find('.children').attr("style", "display: block")
        $(this).find('.children').css("top",xy['top'] - 20 + 'px');

    })

    el.addEventListener('mouseout', function () {
        $(this).find('.children').attr("style", "display: none")
    })

    $(el).on('touchstart', function (){
        console.log('Тач отслежен')
        if ($(this).find('.children').css('display') == 'none'){
            $(this).find('.children').slideToggle()
        } else {
            $(this).find('.children').slideToggle()
        };
    });

});


// Transferring data from the form to the cart
//     Processing block of the add product page
    let product_cart_div = document.querySelectorAll('.prod-card-div')
    product_cart_div.forEach(function (el){
        let hidden_quantity_in_cart = $(el).find('#quantity-from-cart')[0]
        let variable_quantity_p = $(el).find('.variable-quantity-p')[0]
        let variable_quantity_span = $(el).find('.variable-quantity')[0]
        let available_quantity = Number($(variable_quantity_span).text())
        let quantity_input = $(el).find('.quantity-input')

        let how_much_can_input = available_quantity - Number($(hidden_quantity_in_cart).text())

        let quantityArrowMinus = $(el).find(" a.quantity-arrow-minus");
        let quantityArrowPlus = $(el).find(".quantity-arrow-plus");
        let form_qu = $(el).find('#basket-form')

        $(variable_quantity_span).text(how_much_can_input)
        $(quantity_input).attr('max', how_much_can_input)

        $(quantity_input).bind('input', function () {
            $(variable_quantity_span).text(how_much_can_input - $(this).val())
        });

        $(quantityArrowMinus).on('click', function (){
            let vall = Number($(quantity_input).val())
            if (vall > 1){
                $(quantity_input).trigger('input', $(quantity_input).val(vall - 1))
            }
        });

        $(quantityArrowPlus).on('click', function (){

            let vall = Number($(quantity_input).val())
            if (vall < Number(available_quantity)){
                $(quantity_input).trigger('input', $(quantity_input).val(vall + 1))
            }
        });

        $(form_qu).submit(function (event){
                event.preventDefault();
                const friendForm = $(this);
                const posting = $.post( friendForm.attr('action'), friendForm.serialize() );
                posting.done(function(data) {
                    let number_items = data['count']
                    let count_btns = document.querySelectorAll('#count-items')
                    count_btns.forEach(function (el){
                        $(el).text(number_items)
                    });
                    let inp = $(el).find('#id_quantity')
                    $(inp).val('')
                    how_much_can_input = Number($(variable_quantity_span).text())
                    available_quantity = Number($(variable_quantity_span).text())

                });
            });
    });

    // Place an order from the cart page using a promo code
    let ordering_div = $('#finel-price')
    let ordering_btn = $(ordering_div).find('#an_order_btn')[0]
    const ordering_form = $(ordering_div).find('form')
    $(ordering_btn).on('click', function (el){
        // el.preventDefault()
        const posting = $.post( $(ordering_btn).attr('href'), ordering_form.serialize());
        posting.done(function(data) {
            console.log('Готово')
        })
    });


    // delete from cart

    let all_items_carts = document.querySelectorAll('#item-cart-in-cart')

    all_items_carts.forEach(function (el){
        let btn = el.querySelector('.remove-item-cart')
        btn.addEventListener('click', function (event){
            event.preventDefault();
            let url = $(this).attr('href')
            $.ajax({
                url: url,
                method: 'get',
                dataType: 'json',
                success: function (data){
                    let number_items = data['count']
                    let total_price = data['total_price']
                    let count_btns = document.querySelectorAll('#count-items')
                    count_btns.forEach(function (el){
                        $(el).text(number_items)
                    });
                    let str_total = $('#finel-price').find('.total-price').text().split(' ')

                    let change_total = str_total[0] + ' ' + total_price
                    $('#finel-price').find('.total-price').text(change_total)

                    $(el).hide('fast', function(){
                        $(this).remove();
                    });
                }
            })
        });
    });

    // login button

    function clickBtnSingIn (el) {
        console.log('Нажал на вход ')
        let str_height = $(window).height()
        let background_muted = $('.muted-background-login-block')
        $('.login_block').css('top', (str_height/2)/2)
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

    $(document).on('click', function (e){
        let background_muted = $('.muted-background-login-block')
        let div = $('.login_block')
        let div_btn_log = $('#btn-in')
        let mobile_btn = $('#btn-in-mobile')


        if ($(div).css('display')!='none'
        && div.has(e.target).length === 0
        && div_btn_log.has(e.target).length === 0
        && mobile_btn.has(e.target).length === 0)
        {
            $('.login_block').hide('fast')
            $(background_muted).hide('fast')
        }

    });



    // Site login processing
    $('.form-btn-submit').on('click touchstart', function (el){
        // let form = document.querySelector('#login-form-main')
        let form = document.querySelectorAll('#login-form-main')
        form.forEach(function (el){
            if ($(el).is(':visible')){
                form = el
            }
        });
        $(form).submit(function (event){
            // event.stopPropagation()
            event.preventDefault();
            const logForm = $(this);
            const posting = $.post( logForm.attr('action'), logForm.serialize());
            posting.done(function(data) {
                let background_muted = $('.muted-background-login-block')

                $(background_muted).hide('fast')
                let inputs = document.querySelector('.login_block').querySelectorAll('input.form-control')
                inputs.forEach(function (el){
                    $(el).val('')
                });

                $('.login_block').attr('hidden','hidden')
                location.reload()
                console.log('ушло успешно')
            });
            posting.fail(function(data) {
                $('.it-if-error').css('display', 'block')
                console.log('Что то не так')
            });
        });
    });




    if ($('#checkMe').is(':checked')){
        console.log('Выбрано')
    }

    // Remove all items from the cart
    $('#main-check-cart').on('click', function (el){
        let all_cheks = document.querySelectorAll('#check-in-card')
        if ($(this).is(':checked')){
            all_cheks.forEach(function (check){
                if ($(check).is(':checked')){
                } else {
                    $(check).trigger('click')}
            });
        } else {
            all_cheks.forEach(function (el){
                $(el).trigger('click');
                if ($(el).is(':checked')){
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

                    if ($('#main-check-cart').is(':checked')){
                        console.log('Почему то сработало')
                        $('#main-check-cart').trigger('click')
                    }

                    let number_items = data['count']
                    let total_price = data['total_price']
                    let count_btns = document.querySelectorAll('#count-items')
                    count_btns.forEach(function (el){
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

    changer.forEach(function (el){
        let form_div = $(el).find('#quantity-update-form')[0]
        let checkbox = $(form_div).find('form').find('#quantity-update')
        let number_int =  $(form_div).find('.quantity-input')[0]
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

        $(number_int).keydown(function (e){
            if(e.keyCode === 13){
                e.preventDefault()
            }
        });

        $(number_int).attr('max', $(hidden_quantity).text())

        $(quantityArrowMinus).on('click', function (){
            let vall = Number($(number_int).val())
            if (vall > 1){
                $(number_int).trigger('input', $(number_int).val(vall - 1))
            }
        });

        $(quantityArrowPlus).on('click', function (){

            let vall = Number($(number_int).val())
            if (vall < Number($(hidden_quantity).text())){
                $(number_int).trigger('input', $(number_int).val(vall + 1))
            }
        });


        $(number_int).bind('input', function () {

            if (Number($(this).val())<=Number($(hidden_quantity).text())){

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

                setTimeout(function (){
                    $(final_residue).attr('style','color:' + old_color)
                }, 2500)
            }
        });
    });




    // Delivery page unit


    let block = $('#changeable-js-block')[0]
    let block_input = $('#index-input')[0]
    let standart_style_input = $(block_input).css('border')
    let label_input = $('#changeable-js-block').find('label')[0]
    let standart_label_input = $(label_input).text()
    let btn_block = $('#input-delivery-btn')[0]
    let second_step = $('#s-changeable-js-block')
    $(second_step).hide()

    $(block_input).on('input', function (el){

        if ($(this).val().length > 6){
            $(this).css('border', '1px solid red')
            $(label_input).text('Индекс должен состоять из 6 цифр')
            $(label_input).css('color', 'red')

        } else {
            $(this).css('border', standart_style_input)
            $(label_input).text(standart_label_input)
            $(label_input).css('color', 'black')
        }

        if ($(this).val().length == 6){
            $(btn_block).attr('style', 'display: block')
        } else {
            $(btn_block).attr('style', 'display: none')
        }
    });

    function yaMapCaller(data, cdek, phone, full_cdek){

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

                        if ($("#map-block").length){
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
                            '<p class="w-100 text-center"><small>Заполните данные для доставки</small></p>' +
                            '<p class="w-100 text-center error-info-block" style="color: red"></p>' +
                            '<input class="form-control w-50 my-1 mx-3 phone-input"  required type="phone" placeholder="Телефон.."><br>' +
                            '<input class="form-control my-1 mx-3 w-50 f-name" type="text" required  placeholder="Ф.И.О."><br>' +
                            '</div>' +
                            '<div class="d-flex flex-wrap justify-content-center">' +
                            '<a href="#" class="btn btn-warning btn-sm mt-2 mb-1 call-ajax ">Подтвердить</a><br>' +
                            '<a href="#" class="text-muted w-100 text-center " style="text-decoration: none;">' +
                            '<small class="cancel-btn">Отмена</small></a>' +
                            '</div>' +
                            '</div>')

                        $('#map').append(block)
                        $('#map-block').css('z-index', '3500')
                        $(block).offset({top: offset.top, left: offset.left})


                        // Теперь прописать отслеживание нажатии клавиши да и замена данных на форму
                        $('#map-yes').on('click', function (){
                            $(block).remove();
                            $('#map').append(input_block);
                            $(input_block).offset({top: offset.top, left: offset.left});
                            $(input_block).css('width', map_width);
                            if (phone!=null){
                                $('.phone-input').val(phone)
                            }
                             $('.cancel-btn').on('click', function (){
                                $(input_block).remove()
                             });

                            $('.call-ajax').on('click', function (){

                                if ($('.f-name').val() && $('.phone-input').val()){
                                    $('#full-name-delivery').val($('.f-name').val())
                                    $('#phone-delivery').val($('.phone-input').val())
                                    $('#street-delivery').val(full_cdek[objectId]['address'])

                                    const order_form = $('#order-delivery-main-form')[0]
                                    const action = $(order_form).attr('action')
                                    const post_it = $.post(action, $(order_form).serialize());
                                    post_it.done(function (data) {
                                        console.log('Формочка успешно ушла')
                                    });
                                    post_it.fail(function (data) {
                                        console.log('Ошибка где то кроется')
                                    })

                                } else {
                                    $('.error-info-block').append('<small>Для того что бы продлолжить, ' +
                                        'необходимо заполнить все поля</small>')
                                }
                            });



                        });
                        // Отслеживание клавиши нет
                        $('#map-no').on('click', function (){
                            $(block).remove();


                        });

                        $(window).on('resize', function(){
                            let offset = $('#map').offset()
                            if ($(block).length){
                                $(block).offset({top: offset.top, left: offset.left})
                        }

                            if ($(input_block).length){
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

    $(btn_block).on('click', function (event){
        event.preventDefault()
        const form = $(block).find('form')[0]
        let action = $(form).attr('action')
        const posting = $.post(action, $(form).serialize());
        posting.done(function(data){
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

            if (pochta['city'] && !!full_cdek.length){
                // тут функционал при наличии данных и от сдек и от почты
                $('#region-delivery').val(pochta['region'])
                $('#city-delivery').val(pochta['city'])
                $('#index-delivery').val(pochta['index'])

                yaMapCaller(data, cdek, phone, full_cdek)

            // cdek delivery block with display on the map

            } else if (pochta['city']){
                // тут возврат сообщения что сдека нет
                $('#radio-dek').remove()
                $('#block-1').remove()
                $('#radio-pochta').remove()
                $('#block-2').fadeIn();
                $('#region-delivery').val(pochta['region'])
                $('#city-delivery').val(pochta['city'])
                $('#index-delivery').val(pochta['index'])
                $('#delivery-name').val(2)
                $('#delivery_price').text('+ стоимость доставки: ' + pochta_price)
                if (phone != null) {
                    $('#phone-delivery').val(phone)
                }



                console.log('Есть только почта')
            } else if (!!full_cdek.length){
                // тут что то непонятное, скорее всего почта легла, просто автозаполнение нужно убрать
                // оставить ручной или сделать автозаполнение из данных сдека
                $('#region-delivery').val(full_cdek[0]['region'])
                $('#city-delivery').val(full_cdek[0]['city'])
                $('#index-delivery').val(full_cdek[0]['index'])

                yaMapCaller(data, cdek, phone, full_cdek)
                console.log('Есть только сдек')
            } else {
                // ну а тут или чел ввел не корректный индекс, или все полегло, просто
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
                    if ($(this).val() == 2){
                        $('#delivery_price').text('+ стоимость доставки: ' + pochta_price)
                    }

                    if ($(this).val() == 1){
                        $('#delivery_price').text('+ стоимость доставки: ' + cdek_price)
                    }
                });
                console.log('Нет данных ни по сдеку ни по почте')
            }

        });

        posting.fail(function(data) {
            console.log('Что то не так')
            console.log(data)
            // Тут стоит прописать блок ручного ввода данных на тот случай если апишки не работают.
        });

    });


    //     Тут объяснять нечего
    // Единственное в условиях в блоке обработке клика при отправке индекса, есть ответвление
    // при котором от сервера не пришел ответ ни по почте, ни по сдеку, там формируются в форму
    // собственные радио бАтоны. тут отслеживается есть ли такие в форме и если да, выбраны ли те
        $('#main-form-btn').click(function (event) {
            // event.preventDefault()
            const order_form = $('#order-delivery-main-form')[0]
            const action = $(order_form).attr('action')


            if ($('input[name="radi"]').length){
                if (!($('input[name="radi"]').is(':checked'))){
                    event.preventDefault()
                    let rd = $('input[name="radi"]')[0]
                    let alert = $('<div class="alert alert-warning alert-dismissible fade show" role="alert">\n' +
                        '<strong>выберете способ доставки</strong>' +
                        '</div>')
                    $(rd).before(alert)
                    setTimeout(function (){
                        $(alert).remove()
                    }, 2000)
                    return

                }
            }

            const post_it = $.post(action, $(order_form).serialize());
            post_it.done(function (data) {
            });
            post_it.fail(function (data) {
            });



        });

        $('input[name="radio"]').click(function(){
            let cdek_price = $('#cdek-price').text() + ' руб.'
            let pochta_price = $('#pochta-price').text() + ' руб.'
            let target = $('#block-' + $(this).val());

            $('#delivery-name').val($(this).val())

            if ($(this).val() == 2) {
                $('#delivery_price').text('+ стоимость доставки: ' + pochta_price)
            }

            if ($(this).val() == 1) {
                $('#delivery_price').text('+ стоимость доставки: ' + cdek_price)
            }


            $('.block-text-delivery').not(target).hide(0);
            target.fadeIn(500);
    });

        // Клавиша наверх
        $('#button-up').click(function (el) {
            el.preventDefault()
            $('body,html').animate({
                scrollTop: 0
            }, 500);
            return false;
    });


    // Resize empty content divs and change their height so that the footer is at the bottom of the screen
    // if ($('.breadcrumbs-div').length){
    //     let content_div = $('.breadcrumbs-div').next('div.border-bottom').next()
    //     if ($(content_div).height() < ($(window).height() / 1.8)) {
    //
    //         $(content_div).height(($(window).height() / 2.2))
    //     }
    //
    // } else if ($('.news-block').length){
    //     let content_div = $('.news-block').next()
    //     if ($(content_div).height() < ($(window).height() / 1.8)) {
    //
    //         $(content_div).height(($(window).height() / 2.2))
    //     }
    // } else if ($('.message-div').length){
    //     let content_div = $('.news-block').next()
    //     if ($(content_div).height() < ($(window).height() / 1.8)) {
    //
    //         $(content_div).height(($(window).height() / 2.2))
    //     }
    // } else {
    //     let content_div = $('.burger-muted-background').next()
    //     if ($(content_div).height() < ($(window).height() / 1.8)) {
    //
    //         $(content_div).height(($(window).height() / 2.2))
    // }
    // }


    // Changes for mobile permissions
    $('.icon-search-mobile').on('click', function (){
        $('.search-input').slideToggle()
    });

    console.log($(document).outerHeight())
    console.log($(document).height())
    ($(document).outerHeight()).resize(function (){
        console.log($(document).outerHeight())
    })

    ($(document).height()).resize(function (){
        console.log($(document).height())
    })


});

