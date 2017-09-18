/**
 * Created by Winsom on 2015/10/22.
 */
django.jQuery(function() {
    //get all td in a row which has a flag that order is closed
    var rows = django.jQuery('#result_list tr').has('td.field-is_closed img[alt="True"]').children('td:gt(0)');
    //disable input options
    rows.children('input').not('input.action-select').attr('disabled', 'disabled');
    rows.children('div').children('select').attr('disabled', 'disabled');
    //hide foreign key options
    //rows.children('.related-widget-wrapper').children().hide();
});
