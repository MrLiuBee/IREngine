// JavaScript Document
var date = new Date(),
    year = date.getFullYear(),
    month = date.getMonth(),
    day = date.getUTCDate(),
    months = [ "Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sept", "Oct", "Nov", "Dec"];

document.getElementById('daymonth').innerHTML = months[month] + " " + day;
document.getElementById('year').innerHTML = year;

var clockH = $(".hours");
var clockM = $(".minutes");

function time() {     
  var d = new Date(),
      s = d.getSeconds() * 6,
      m = d.getMinutes() * 6 + (s / 60),
      h = d.getHours() % 12 / 12 * 360 + (m / 12);  
    clockH.css("transform", "rotate("+h+"deg)");
    clockM.css("transform", "rotate("+m+"deg)");  
}

var clock = setInterval(time, 1000);
time();