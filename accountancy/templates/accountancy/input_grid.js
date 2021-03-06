$(document).ready(function() {

    var line_form_prefix = "{{ line_form_prefix }}" || "form";

    // for entering transaction lines only
    var main_grid = new Grid({
        prefix: line_form_prefix,
        form_identifier: ".formset", // pluralise
        order_lines: true,
        order_identifier: ".ordering",
        empty_form_identifier: ".empty-form",
    });

    var selectized_menus = {}; // keep track of the menus we create so we can destroy them also when removing the lines

    function destory_selectized_menus($tr) {
        // loop through input elements in row
        $tr.find(":input").each(function(index, elem) {
            if (elem.name in selectized_menus) {
                selectized_menus[elem.name][0].selectize.destroy();
                delete selectized_menus[elem.name];
            }
        });
    }

    $(document).on("mousedown", "div.lines :input[data-selectize-type='nominal']", function(e) {
        e.preventDefault();
        if (!$(this).hasClass("selectized")) {
            var s = input_grid_selectize.nominal(this);
            selectized_menus[this.name] = s;
        }
    })

    $(document).on("mousedown", "div.lines :input[data-selectize-type='vat']", function(e) {
        e.preventDefault();
        if (!$(this).hasClass("selectized")) {
            var s = input_grid_selectize.vat(this);
            selectized_menus[this.name] = s;
        }
    })

    function two_decimal_places($input) {
        if(!$input){
            return;
        }
        var val = $input.val();
        if(val == ""){
            return;
        }
        val = +val;
        if(typeof val == 'number'){
            val = parseFloat(val).toFixed(2);
            $input.val(val);
        }
    }

    main_grid.add_callback = function(new_line) {
        return;
    };

    $(".add-lines").on("click", function(event) {
        main_grid.add_line();
    });

    $(".add-multiple-lines").on("click", function(event) {
        var $target = $(event.target);
        var lines = $target.attr("data-lines");
        if (lines) {
            lines = +lines;
            main_grid.add_many_lines(lines);
        }
    });

    {% if edit %}

    $(document).on("click", "td.col-close-icon", function(event) {
        var $this = $(this);
        var $tr = $(this).parents("tr");
        var val = $tr.find("input.delete-line").get(0).checked;
        if (val) {
            $(this).parents("tr").find("input.delete-line").prop("checked", false);
            $tr.removeClass("deleted-row");
        } else {
            // if the line is not saved in the DB already just delete the line / row / form
            var id_input_field = $tr.find(":input").filter(function() {
                return this.name.match(/^line-\d+-id$/);
            });
            if (id_input_field && !id_input_field.val()) {
                main_grid.delete_line($this);
                destory_selectized_menus($(this).parents("tr").eq(0));
            } else {
                $(this).parents("tr").find("input.delete-line").prop("checked", true);
                $tr.addClass("deleted-row");
            }
        }
        calculator.calculate_totals();
    });

    // in case the server returns errors loop through lines with deleted set
    // and change color
    $("td.col-close-icon").each(function() {
        var $tr = $(this).parents("tr");
        var val = $tr.find("input.delete-line").prop("checked");
        if (val) {
            $tr.addClass("deleted-row");
        } else {
            $tr.removeClass("deleted-row");
        }
    });

    {% else %}

    $(document).on("click", "td.col-close-icon", function(event) {
        main_grid.delete_line($(this));
        destory_selectized_menus($(this).parents("tr").eq(0));
        event.stopPropagation();
    });

    {% endif %}

    $("html").on("click focusin", function() {
        $("table.line td").find("*").removeClass("data-input-focus-border");
        $(":input[type='number']").each(function() {
            two_decimal_places($(this)); // could be slow
        });
    });

    $(document).on("click focusin", "table.line td", function(event) {
        $("td").find("*").not($(this)).removeClass("data-input-focus-border");
        if ($(this).find(":input").hasClass("can_highlight")) {
            $(this).find(":input.can_highlight").addClass("data-input-focus-border");
            // the above won't work though for adding the border to the input with the selectized widget
            // so... we do this
            $(this).find("div.selectize-input").addClass("data-input-focus-border");
        }
        event.stopPropagation();
    });

    $(document).on("change", ":input[type='number']", function() {
        two_decimal_places($(this));
    });

});