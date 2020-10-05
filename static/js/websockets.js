
var socket = io.connect('http://' + document.domain + ':' + location.port);

$(document).ready(function()
{

    socket.on('r_obtenercalle', function(data)
    {
        console.log("recibido ");
        document.getElementById("calle").value = data["calle"];
        $("#calle").parent().addClass("fl-is-active fl-has-focus");
        document.getElementById("numero").value = data["numero"];
        $("#numero").parent().addClass("fl-is-active fl-has-focus");
        document.getElementById("cp").value = data["cp"];
        $("#cp").parent().addClass("fl-is-active fl-has-focus");
        document.getElementById("localidad").value = data["localidad"];
        $("#localidad").parent().addClass("fl-is-active fl-has-focus");

    });




});

function obtenercalle()
{

    if(navigator.geolocation)
    {
        navigator.geolocation.getCurrentPosition(function(position)
        {
            console.log("dentroasasd!");
            document.getElementById("latitude_gps").value =  position.coords.latitude.toString();
            document.getElementById("longitude_gps").value =  position.coords.longitude.toString() ;
            document.getElementById("precision").value = position.coords.accuracy.toString() + " metros";
            socket.emit("obtenercalle", position.coords.latitude, position.coords.longitude );

        }, function(error)
        {

            switch(error.code)
            {
                case error.PERMISSION_DENIED:
                     document.getElementById("latitude_gps").innerHTML = "User denied the request for Geolocation.";
                break;
                case error.POSITION_UNAVAILABLE:
                     document.getElementById("latitude_gps").innerHTML = "Location information is unavailable.";
                break;
                case error.TIMEOUT:
                     document.getElementById("latitude_gps").innerHTML = "The request to get user location timed out.";
                break;
                default:
                     document.getElementById("latitude_gps").innerHTML = "An unknown error occurred.";
                break;
            }

        }, {maximumAge:10000, timeout:5000, enableHighAccuracy: true});

    } else {
        alert("Sorry, your browser does not support HTML5 geolocation.");
    }
}

