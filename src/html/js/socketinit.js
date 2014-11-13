var namespace = '/test'; // change to an empty string to use the global namespace

// the socket.io documentation recommends sending an explicit package upon connection
// this is specially important when using the global namespace
var socket = io.connect('http://' + document.domain + ':' + location.port + namespace, {
                            "connect timeout": 300,
                            "close timeout": 60,
                            "hearbeat timeout": 40,
                            "transports": ["htmlfile", "xhr-polling", "jsonp-polling"]
                        });