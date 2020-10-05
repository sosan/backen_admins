    function cambioinputs(param)
    {
        if (param.value !== "")
        {
            param.parentElement.parentElement.lastElementChild.style.cssText = "display: none;";
        }

    }

    let current_fase = 0;

    function cambiotipocasa(param)
    {
        var spans = $("span[class='error']");
        for (var i = 0; i < spans.length; i++)
        {
            spans[i].style.cssText = "display: none;";

        }

    }

    function show_siguientefase()
    {
        let current_step = $(".step")[current_fase];
        current_step.style.cssText = "display: none;";
        current_step.className = "step wizard-step";

        current_fase++;
        if (current_fase > 4) {
            current_fase = 4;
        }

        let next_current_step = $(".step")[current_fase];
        next_current_step.style.cssText = "display: block;";
        next_current_step.className = "step wizard-step current";
        showButtons();


    }

    function show_anteriorfase()
    {
        let current_step = $(".step")[current_fase];
        current_step.style.cssText = "display: none;";
        current_step.className = "step wizard-step";

        current_fase--;
        if (current_fase < 0) {
            current_fase = 0;
        }

        let next_current_step = $(".step")[current_fase];
        next_current_step.style.cssText = "display: block;";
        next_current_step.className = "step wizard-step current";
        showButtons();

    }

    function comprobar_fase(min, max)
    {

        let elementos = $("input");

        let siguientefase = true;
        let checkbox_correcto = 0;
        let radiobox_correcto = 0;
        let check_radiobox = false;
        let check_checkbox = false;
        let radioboxminelement = -1;
        let checkboxminelement = -1;
        for (var i = min; i < max; i++)
        {
            if (elementos[i].type === "text" || elementos[i].type === "number")
            {
                if (elementos[i].value === "")
                {
                    elementos[i].classList.add("error");
                    elementos[i].parentElement.parentElement.lastElementChild.style.cssText = "display: block;";
                    siguientefase = false;
                }
                else
                {
                    elementos[i].classList.remove("error");
                    elementos[i].parentElement.parentElement.lastElementChild.style.cssText = "display: none;";


                }

            }
            else if (elementos[i].type === "radio")
            {
                check_radiobox = true;
                if (radioboxminelement === -1)
                {
                    radioboxminelement = i;
                }

                if (elementos[i].checked === true)
                {
                    radiobox_correcto++;


                }

            }
            else if (elementos[i].type === "checkbox")
            {
                check_checkbox = true;
                if (checkboxminelement === -1)
                {
                    checkboxminelement = i;
                }


                if (elementos[i].checked === true)
                {
                    checkbox_correcto++;

                }

            }


        }

        if (check_radiobox === true)
        {
            if (radiobox_correcto > 0)
            {
                elementos[radioboxminelement].classList.remove("error");
                elementos[radioboxminelement].parentElement.lastElementChild.style.cssText = "display: none;";
            }
            else
            {
                elementos[radioboxminelement].classList.add("error");
                elementos[radioboxminelement].parentElement.lastElementChild.style.cssText = "display: block;";
                siguientefase = false;

            }


        }

        if (check_checkbox === true)
        {

            if (checkbox_correcto > 0)
            {
                elementos[checkboxminelement].classList.remove("error");
                elementos[checkboxminelement].parentElement.lastElementChild.style.cssText = "display: none;";

            }
            else
            {
                elementos[checkboxminelement].classList.add("error");
                elementos[checkboxminelement].parentElement.lastElementChild.style.cssText = "display: block;";
                siguientefase = false;

            }

        }

        if (siguientefase === true)
        {
            show_siguientefase();
        }


    }

    // $(document).ready(function()
    // {
    //     $("#forward").click(function()
    //     {
    //         alert($("#contenido_central").scrollTop() + " px");
    //         $("#contenido_central").scrollTop(0,0);
    //     });
    // });


    $('#forward').click(function()
    {
       $("#contenido_central").scrollTop(0,0);

        switch(current_fase)
        {
            case 0: comprobar_fase(0, 4); break;
            case 1: comprobar_fase(4, 8); break;
            case 2: comprobar_fase(8, 13); break;
            case 3: comprobar_fase(13, 20); break;
            case 4: break;
            case 5: break;


        }


    });

    $('#backward').click(function()
    {
        $("#contenido_central").scrollTop(0,0);
        show_anteriorfase();

    });


    function formatform() {
        var floatlabels = new FloatLabels( "form", {
                style: 1
        });

    }

    $(document).ready(formatform());
    $(document).ready(showButtons());

    function showButtons()
    {

        let back = document.getElementsByName("backward");
        let frw = document.getElementsByName("forward");
        let pro = document.getElementsByName("process");

        switch(current_fase)
        {
            case 0:
                back[0].disabled = true;
                pro[0].disabled = true;
                frw[0].disabled = false;

            break;
            case 1:
            case 2:
            case 3:
                back[0].disabled = false;
                pro[0].disabled = true;
                frw[0].disabled = false;
            break;

            case 4:
                back[0].disabled = false;
                pro[0].disabled = false;
                frw[0].disabled = true;
            break;


        }

    }


    $(document).ready(showPosition());


    function showPosition()
    {

        if(navigator.geolocation)
        {
            navigator.geolocation.getCurrentPosition(function(position)
            {
                document.getElementById("latitude_gps").value =  position.coords.latitude.toString();
                document.getElementById("longitude_gps").value =  position.coords.longitude.toString() ;
                document.getElementById("precision").value = position.coords.accuracy.toString() + " metros";


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


    $.fn.fileUploader = function (filesToUpload, sectionIdentifier)
    {
        var fileIdCounter = 0;

        this.closest(".files").change(function (evt)
        {

            var output = [];
            var promises = [];

            for (var i = 0; i < evt.target.files.length; i++)
            {

                let filePromise = new Promise(resolve =>
                {
                    console.log("promise inside=>");
                    let reader = new FileReader();
                    reader.readAsDataURL(evt.target.files[i]);

                    reader.onload = () => resolve(reader.result);

                });
                promises.push(filePromise, evt.target.files[i].name, evt.target.files[i].size);

            }


            Promise.all(promises).then(fileContents =>
            {

                for (var i = 0; i < fileContents.length; i=i+3)
                {
                    fileIdCounter++;
                    var fileId = sectionIdentifier + fileIdCounter;

                    filesToUpload.push({
                        id: fileId,
                        filename: fileContents[i + 1],
                        datafile: fileContents[i + 0]
                    });

                    var removeButton = '<button type="button" class="removeFile btn btn-danger" data-fileid="' + fileId + '"> Quitar </button><br><br>';

                    let size = "";
                    if (fileContents[i + 2] === 0)
                    {
                        size = "0 Bytes";
                    }
                    else
                    {
                        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
                        const lent = Math.floor(Math.log(fileContents[i + 2]) / Math.log(1024));
                        size = parseFloat((fileContents[i + 2] / Math.pow(1024, lent)).toFixed(2)) + ' ' + sizes[lent];
                    }

                    output.push('<li class="tx"><img src="' + fileContents[0 + i]  + '" width="100px" height="100px"><b>' +
                     escape(fileContents[i+ 1]) + '</b> - ' + size + '. &nbsp; &nbsp; ' + removeButton + '</li>');


                }
                $(this).children(".fileList").append(output.join(""));
                    evt.target.value = null;

             });

        });

        $(".removefile").click( function (e)
        {
            e.preventDefault();

            var fileId = $(this).parent().children("a").data("fileid");

            for (var i = 0; i < filesToUpload.length; ++i)
            {
                if (filesToUpload[i].id === fileId)
                    filesToUpload.splice(i, 1);
            }


            $(this).parent().remove();
        });

        this.clear = function ()
        {
            for (var i = 0; i < filesToUpload.length; i++) {
                if (filesToUpload[i].id.indexOf(sectionIdentifier) >= 0)
                    filesToUpload.splice(i, 1);
            }

            $(this).children(".fileList").empty();
        };

        return this;
    };

    (function () {
        var filesToUpload = [];

        var files1Uploader = $("#files1").fileUploader(filesToUpload, "files1");

        $("#process").click(function (e)
        {
            procesarFormulario("/profile/alta", e);
        });

        $("#process_modificado").click(function (e)
        {
            procesarFormulario("/profile/item_modificado", e);
        });

        function procesarFormulario(uri, e)
        {
            e.preventDefault();
             var formData = new FormData(document.getElementById("wrapped"));

            for (var i = 0; i < filesToUpload.length; i++) {

                formData.append("files_" + i + "_datafile", filesToUpload[i].datafile);
                formData.append("files_" + i + "_filename", filesToUpload[i].filename);

            }

            formData.append("files_len", filesToUpload.length.toString());

            $.ajax({
                url: uri,
                data: formData,
                enctype: 'multipart/form-data',
                processData: false,
                contentType: false,
                type: "POST",
                success: function (resp) {
                    $("#contenido_central").scrollTop(0, 0);

                    current_fase = 0;
                    let color_errores = "alert-success";
                    switch (resp["errores"])
                    {
                        case 1:
                            document.getElementById("wrapped").reset();
                            files1Uploader.clear();
                        break;
                        case 2: //no_insertado
                        case 4: //no_actualizado
                        case 5: //duplicado
                            color_errores = "alert-warning";
                            break;
                        default:
                            color_errores = "alert-warning";
                            break;
                    }

                    let middlewizard = document.getElementById("middle-wizard");
                    middlewizard.children[4].className = "submit step wizard-step";
                    middlewizard.children[4].style.cssText = "display: none;";

                    middlewizard.children[0].className = "step wizard-step current";
                    middlewizard.children[0].style.cssText = "display: block;";

                    let back = document.getElementsByName("backward");
                    let frw = document.getElementsByName("forward");
                    let pro = document.getElementsByName("process");

                    back[0].disabled = true;
                    pro[0].disabled = true;
                    frw[0].disabled = false;

                    showPosition();
                    const out = '<h4 class=\'alert ' + color_errores + ' quitadotop\' id=\'success-alert\' style=\'display: block; opacity: 100;\'></h4>';
                    $("#mostrar_resultado").append(out);

                    let elemento = document.getElementById("success-alert");

                    elemento.innerHTML += resp.data;


                    setTimeout(function () {
                        $("#success-alert").remove();
                    }, 4000);


                },
                error: function (data) {
                    alert("ERROR - " + data.responseText);
                }
            });

        }

    })();
