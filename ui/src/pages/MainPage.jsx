import React from 'react';
import _ from 'lodash';
import { Route, BrowserRouter } from "react-router-dom";
import ReactDOM from "react-dom";


import {
    MainPageLayout,
    Link,
    FlexLayout,
    StackingLayout,
    NavBarLayout,
    Menu,
    MenuItem,
    SettingsIcon,
    MenuController,
    ThemeManager,
    ContainerLayout,
    Button,
    Table,
    Alert,
    Radio,
    Favorite,
    MagGlassIcon,
    MenuIcon,
    Input,
    AlertIcon,
    Badge,
    Pagination,
    TextLabel,
    Progress,
  } from "@nutanix-ui/prism-reactjs";
  import Login from './Login.jsx';

const QUOTA_URL = '/quota';
const LOGIN_URL = '/login';

export default class MainPage extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            openMenu : false,
        }

    }
    renderBody() {
    
      const login = () => {
          return (
            <FlexLayout style={ { 'height': '100%'} }>
            <Login 
            history={this.props.history}
            pathname={this.props.pathname}
            />
          </FlexLayout>
          )
      }
    const body = (
        <div style={{ height: '100%' }}>
          <Route exact path={LOGIN_URL} render={login} />
        </div>
      );
      return body;
    }

    render() {
        const account = (
          <div
            overlay={
            <Menu padding="10px-0px" oldMenu={false} theme="dark"
              onClick={(e) => {
                  switch(e.key) {
                    case "logout": 
                      this.logout();
                      break;
                  }         
                }
              }
            >
              <MenuItem key="logout">Logout</MenuItem>
            </Menu>
            }
            title={
              <Link type="expandable" style={{ color: ThemeManager.getVar('gray-3') }}>
                {this.state.profile.username}
              </Link>
            }
          />
        );
        const header = (
          <NavBarLayout 
            accountInfo={account}
            menuIcon={
              <MenuController 
                onClick={ this.toggleMenuState }
                open={ this.state.openMenu }
              />
            }
          />
        );
        const leftPanel = (
          <Menu padding="20px-0px" 
            oldMenu={false} 
            theme="dark"
            onClick={this.handleMenuClick}
            activeKeyPath={[this.state.menuKeyPath]}
          >
            <MenuItem key={LOGIN_URL}>Manage De</MenuItem>        
          </Menu>
        );
    
        return (
          <MainPageLayout
            style={ { 'overflow': 'auto' } }
            fullPage={ true }
            header={ header }
            leftPanel={ leftPanel }
            leftPanelVisible={ this.state.openMenu }
            oldMainPageLayout={ false }
            body={ this.renderBody() }
          />
        )
    }
}


