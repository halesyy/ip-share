const express = require("express")
const app = express()
const port = process.env.PORT || 80;
const ejs = require("ejs")
const cors = require("cors")
const fs = require("fs")

app.use(cors())

app.set("view engine", ejs)
// app.use(express.static('bridges'))
// app.use(express.static('views'))
app.use('/static', express.static('static'))
app.use('/bridges', express.static('bridges'))

app.get("/", (req, res) => {
  res.send("success, app working");
})

global.current_ip = "no-ip-yet, check back in 5 minutes";

app.get("/set-public-ip/:ip", (req, res) => {
  global.current_ip = req.params.ip;
  res.send("success");
});

app.get("/public-ip", (req, res) => {
  res.send(global.current_ip)
});

app.listen(port, () => {
  console.log(`Hosted on port ${port}`);
})
