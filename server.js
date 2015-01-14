var express = require('express');
var app = require('connect');
var serveStatic = require('serve-static');
var request = require('request');
//var errorhandler = require('errorhandler');
var app = express();
var http = require('http');
var path = require('path');

var httpProxy = require('http-proxy');
var proxy = httpProxy.createProxyServer({});

//app.use(app.router);
var baseUrl = "http://localhost:8983/solr";
var port = 3334;
if (process.argv.length > 0){
    process.argv.forEach(function (val, index, array) {
        console.log(index + ': ' + val);
        if (val.indexOf("--port") != -1){
            port = parseInt(process.argv[index + 1]);
            console.log("port: " + port);
        } else if (val.indexOf("--solr") != -1){
            baseUrl = process.argv[index + 1];
        }
    });
}
console.log("Listening on port: " + port + " and proxying to base URL: " + baseUrl);
app.set('port', port);

app.use('/solr', function(req, res) {
	var url = baseUrl + req.url;
	console.log('Proxying to ' + url);
	req.pipe(request({
		    "url": url,
			"qs": req.query,
			"method": req.method
			}, function(err, errRes){
		    if(err){
			console.log("Proxy =>" + err);
			res.send('Proxy => ' + err);
		    }
		})).pipe(res);
    });
app.use(serveStatic(path.join(__dirname, 'static')));
app.use(require('errorhandler'));

http.createServer(app).listen(app.get('port'), function(){
	console.log('Dev server listening on port ' + app.get('port'));
    });
