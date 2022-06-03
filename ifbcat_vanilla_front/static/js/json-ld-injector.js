$(document).ready(function(){
    $("[data-json-ld-uri]").each(function(i,e){
        inject_json_ld_in_header_for(e);
    });
});

function inject_json_ld_in_header_for(elt){
    $.ajax({
        type: "GET",
        url: $(elt).data("jsonLdUri"),
        success : function(data) {
            var script = document.createElement('script');
            script.type = 'application/ld+json';
            script.innerHTML = JSON.stringify(data);
            document.getElementsByTagName('head')[0].appendChild(script);
        },
        error : function(xhr, ajaxOptions, thrownError) {
        }
    });
}