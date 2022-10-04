capkpi.ready(function() {
    // bind events here
    $(".page-header-actions-block .btn-primary, .page-header-actions-block .btn-default").addClass('hidden');
    $(".text-right .btn-primary").addClass('hidden');

    if (capkpi.utils.get_url_arg('name')) {
        $('.page-content .btn-form-submit').addClass('hidden');
    } else {
        user_name = capkpi.full_name
        user_email_id = capkpi.session.user
        $('[data-fieldname="currency"]').val("INR");
        $('[data-fieldname="name_of_applicant"]').val(user_name);
        $('[data-fieldname="email"]').val(user_email_id);
        $('[data-fieldname="amount"]').val(20000);
    }
})