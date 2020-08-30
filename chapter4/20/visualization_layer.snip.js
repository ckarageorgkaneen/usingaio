// Example 4-20. The visualization layer, which is a fancy way of saying “the browser”

/* This is a snippet of the appendixB/3/charts.html JavaScript
   that visualizes the server-sent information */ 

<snip>
/* Create a new EventSource() instance on the /feed URL. The browser will con‐
nect to /feed on our server, (metric_server.py). Note that the browser will auto‐
matically try to reconnect if the connection is lost. Server-sent events are often
overlooked, but in many situations their simplicity makes them preferable to
WebSockets. */
var evtSource = new EventSource("/feed");
evtSource.onmessage = function(e) {
	// The onmessage event will fire every time the server sends data. Here the data // is parsed as JSON.
	var obj = JSON.parse(e.data);
	if (!(obj.color in cpu)) {
		add_timeseries(cpu, cpu_chart, obj.color);
	}
	if (!(obj.color in mem)) {
		add_timeseries(mem, mem_chart, obj.color);
	}
	/* The cpu identifier is a mapping of a color to a TimeSeries() instance (for more
	   on this, see Example B-1). Here, we obtain that time series and append data to // it. We also obtain the timestamp and parse it to get the correct format
	   required by the chart. */
	cpu[obj.color].append(
		Date.parse(obj.timestamp), obj.cpu);
	mem[obj.color].append(
		Date.parse(obj.timestamp), obj.mem);
};
<snip>