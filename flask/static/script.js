
$(document).ready(function(){
    $("#chat_button").click(
        function(){
            $("ol").append("<li>User: "+$("#chat_text").val()+"</li>");
            var msg = {human: $("#chat_text").val()};
            $.post("http://ncataldo.cse356.compas.cs.stonybrook.edu/eliza/DOCTOR/", JSON.stringify(msg))
            .done(
                function(data){
                    var data_json = JSON.parse(data)
                    $("ol").append("<li>Eliza: "+data_json.eliza+"</li>")
                }
            );
        }
    );

});


