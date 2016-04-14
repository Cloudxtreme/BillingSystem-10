$( document ).ready(function() {
    $("input[type=number").focus(function() {
        var self = $(this);
        if(self.val() == "") {
            self.val(".00");
            abc = self;
            self[0].setSelectionRange(0, 0);
        }
    });
});
