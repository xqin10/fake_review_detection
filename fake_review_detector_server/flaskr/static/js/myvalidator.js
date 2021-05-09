$(function () {
    $('form').bootstrapValidator({
        message: 'This value is not valid',
        feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            invalid: 'glyphicon glyphicon-remove',
            validating: 'glyphicon glyphicon-refresh'
        },
        fields: {
            urlinput: {
                message: '',
                validators: {
                    notEmpty: {
                        message: 'Please enter an URL.'
                    },
                    regexp: {
                        regexp: /www\.yelp\.com.*/g,
                        message: 'Please Enter a solid URL for Tripadvisor or Yelp.'
                    },
                    regexp: {
                        regexp: /www\.tripadvisor\.com.*\/(Hotel_Review-|Restaurant_Review-)/g,
                        // regexp: /www.yelp.com.*/g,
                        message: 'Please Enter a solid URL for Tripadvisor or Yelp.'
                    }
                }
            }
        }
    });
});