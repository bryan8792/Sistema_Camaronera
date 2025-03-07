$(function () {

    let dtos = [];
    let obternerIP = () => {
        const result = fetch('https://wtfismyip.com/json')
            // .then(function(response2) {
            //     /*console.log('response2')
            //     console.log(response2.json())*/
            //     const da = response2.json()
            //     console.log('da')
            //     console.log([da])
            //     $.each([da], function (oj, pos) {
            //         console.log('oj')
            //         console.log(oj)
            //         console.log('pos')
            //         console.log(pos.toString())
            //         for (const ojKey in pos.toString()) {
            //             console.log('ojKey')
            //             console.log(ojKey.Object)
            //         }
            //     })
            // })
            .then(response => response.json())
            .then(json => json);

        console.log('El result de la IP')
        console.log(result);

        document.getElementById("infobyip").innerHTML = result;

    }

    obternerIP();
})