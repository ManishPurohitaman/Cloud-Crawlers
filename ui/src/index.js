import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import "@nutanix-ui/prism-reactjs/dist/index.css";
import Home from "./pages/Home.jsx";
import MainPage from "./pages/MainPage.jsx";
import Matching from "./pages/Matching.jsx";
import SubmitModal from "./components/SubmitModal.jsx"
//import Login from "./pages/Login.jsx";
function render() {

function HomePage(props) {
  return (
    <Home pathname={props.location.pathname} history={props.history} />
  )
}


const app = (
    <Router>
      <Switch>
      {/* <Route exact path="/" component={Login} /> */}
      <Route exact path="/home" component={HomePage}/>
      <Route exact path="/home2" component={Matching}/>
      </Switch>
     
    </Router>
);

ReactDOM.render(
    app,
  document.getElementById("root")
);
}
render();
