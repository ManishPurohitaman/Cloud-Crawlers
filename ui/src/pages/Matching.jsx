import * as React from "react";
import { Route, BrowserRouter, Link } from "react-router-dom";
import ReactDOM from "react-dom";
import { getSubscription } from "../util.js";
import _ from 'lodash';
import styles from './home.css';
import SubmitModal2 from "../components/SubmitModal2.jsx";
import { Steps, FlexItem, 
  Modal, FormItemInput,  FormLayout,
  FormSection,
  RadioGroup,
} from '@nutanix-ui/prism-reactjs';

import {
  MainPageLayout,
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
  InputNumber,
  Table,
  Alert,
  Radio,
  Favorite,
  MagGlassIcon,
  MenuIcon,
  Input,
  AlertIcon,
  Badge,
  Select,
  Pagination,
  TextLabel,
  Progress,
  Link as LinkStyle,
  Loader
} from "@nutanix-ui/prism-reactjs";
const customSuffix = (
  <FlexLayout alignItems="center" itemSpacing="10px">
    <TextLabel style={ { borderLeft: '1px solid #b8bfca',
      padding: '5px 0px 5px 10px' } }>GB</TextLabel>
  </FlexLayout>
);

const account = <LinkStyle type="info">cloud_crawlers@nutanix.com</LinkStyle>;

const alerts = (
  <FlexLayout itemSpacing="10px" alignItems="center">
    <AlertIcon size="large" color={ ThemeManager.getVar('red-1') } />
    <Badge count={ 8 } color="red" />
  </FlexLayout>
);
const pagination = {
  total: 10,
  currentPage: 1,
  pageSize: 10
};
const data_c = [
  {
    key: 1,
    label: 'us-east-1'
  }
];
const data_p = [
  {
    key: 1,
    label: 'Compute'
  },
  {
    key: 2,
    label: 'Memory',
  },
  {
    key: 3,
    label: 'General Purpose'
  },
  {
    key: 4,
    label: 'GPU Accelerated'
  }

];

export default class Matching extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      leftPanelVisible: false,
      tableData: [],
      showTable: false,
      visible: false,
      // inputArray: Array(5),
      // inputValue: ''
      vcpu: '',
      memory: '',
      location: 'east-us-1',
      provider: 'AWS'
    };
    this.handleOnClose = this.handleOnClose.bind(this);

    this.gettableData = this.gettableData.bind(this);
    this.handleOnClickMenuIcon = this.handleOnClickMenuIcon.bind(this);
    this.handleOnSelectedChange = this.handleOnSelectedChange.bind(this);

    // this.selectProps = {
    //   rowsData: data_c,
    //   onSelectedChange: this.handleOnSelectedChange,
    //   // We attached to the right-panel to handle the scrolling placement properly.
    //   // getPopupContainer: () => document.querySelector('.right-panel'),
    //   popupProviderProps: { action: 'hover' }
    // }
    // this.selectProps_one = {
    //   rowsData: data_p,
    //   onSelectedChange: this.handleOnSelectedChange,
    //   // We attached to the right-panel to handle the scrolling placement properly.
    //   // getPopupContainer: () => document.querySelector('.right-panel'),
    //   popupProviderProps: { action: 'hover' }

    // }
  }
  handleOnClickMenuIcon() {
    this.setState({
      leftPanelVisible: !this.state.leftPanelVisible
    });
  }
  handleOnClickColumn() {
    this.setState({

    })
  }
  handleOnClose() {
    this.setState({ visible: false })
    this.handleClick()

  }

  // componentDidMount() {
  //   this.gettableData();
  // }

  handleOnSelectedChange(selectedRow) {
    this.setState({ selectedRow });
  }
  gettableData= (provider,instance) =>  {
    console.log(`http://0.0.0.0:8000/api/v1/vm/sizer/matching/${provider}/${instance}`)
    fetch(`http://0.0.0.0:8000/api/v1/vm/sizer/matching/${provider}/${instance}`)
      .then((res) => res.json())
      .then(
        (data) => {
          let subdata = data.data;
          subdata.forEach((item, i) => {
            item.key = i + 1;
          });
          this.setState({
            tableData: subdata,
          });

        },
        (error) => {
          console.log("error");
        }
      );

  }

  handleClick(){
    this.setState({showTable: true})

  }

  displayTable() {
    const columns = [
    {
      title: 'Cloud',
      key:'provider'
    }, {
      title: 'Instance Type',
      key: 'instanceType'
    }, {
      title: 'vCPUs',
      key: 'cpu'
    }, {
      title: 'Memory(GB)',
      key: 'ram'
    }, {
      title: 'Instance Storage',
      key: 'localStorage'
    }, {
      title: 'Cost/hour($)',
      key: 'pricePerHr'
    }, {
      title: 'InstanceCategory',
      key:'instanceCategory'
    }
  ];
    let t ; 
    if (this.state.showTable){
      var provider=this.state.provider
      var instance=this.state.instance
    if(provider!='' && instance!='')
    this.gettableData(provider,instance)
    
      t = (
        <Table
          rowKey="key"
          dataSource={this.state.tableData}
          columns={columns}
        />
      );
    }
    return t;
  }


  render() {
    const menuIcon = <MenuIcon color="dark" onClick={ this.handleOnClickMenuIcon } />;
    const header = (<NavBarLayout
      accountInfo={ account }
      menuIcon={ menuIcon }
      // searchInput={
      //   <Input placeholder="Search Input" theme="dark"
      //     suffix={ <Favorite background="dark" checked={ true } /> }
      //     prefix={ <MagGlassIcon color={ ThemeManager.getVar('gray-2') } /> }
      //   />
      // }
    />);
    const leftPanel = (
      <Menu
        padding="20px-0px"
        style={{ width: "240px" }}
        theme="dark"
      >
        <Link to={`/home`}>
        <MenuItem key={"1"}>Instance Info</MenuItem>
        </Link>
        <Link to={`/home2`}>
        <MenuItem key={"2"}>Matching Instance</MenuItem>
        </Link>
      </Menu>
    );    
    const sort = {
      sortable: ['reserved']
    };
    const sorters = {
      reserved: (a, b) => {
        return a.reserved - b.reserved;
      }
    };
    const rowSelection = {
      selected: []
    };   
    const wrapper = {
      width: '260px'
    }; 
    
    const customSuffix2 = (
      <FlexLayout alignItems="center" itemSpacing="10px">
        <TextLabel style={ {
          borderLeft: '1px solid #b8bfca',
          padding: '5px 0px 5px 10px'
        } }>
          GiB
        </TextLabel>
      </FlexLayout>
    );
    

    // const sample = getSubscription().then((res)=>{return res.body});
    // console.log(sample);
    const body = (
      <div>
        <div className="heading">
          <h1 style={{ textAlign:"center", marginTop: 25, marginBottom:25}}>X Cloud Workload Analyzer - 2</h1>
        </div>
        {/* <div className="filter-wrapper">
          <InputNumber 
            label="Memory"
            suffix={ customSuffix2 } />
          <InputNumber
          label="vCPUs" min={ 1 } max={ 32 } step={ 1 }
          onChange={ this.handleOnChange } inputRef={ this.myInputRef } />
          <Select style={ { maxWidth: '440px' }}
          { ...this.selectProps }
          selectedRow={ this.state.selectedRow }
          />
            <InputNumber 
            label="Instance Storage"
            suffix={ customSuffix2 } />
            <Select style={ { maxWidth: '440px' }}
          { ...this.selectProps_one }
          selectedRow={ this.state.selectedRow }
          />
        </div> */}
        <div className="button-wrapper">
        {/* <FlexLayout padding="20px" >
          <Button>Submit</Button>
        </FlexLayout> */}
         <div>
          <Button type="primary" margin-top='50px'
            onClick={ () => this.setState({ visible: true }) }>
            Enter Instance Details Here!
          </Button>
          <Modal
            visible={ this.state.visible }
            title="Input"
            onClose={ this.handleOnClose }
            closeIconProps={ { 'data-test': 'my-close-icon-data-test' } }
            primaryButtonOnClick={ this.handleOnClose }
          >
            <FormLayout>
            <FormSection title="General Configuration">
                 <RadioGroup name="provider"
        layout={ RadioGroup.RadioGroupLayout.HORIZONTAL }
        onChange={ (event) => this.setState({ provider: event }) }
        selectedValue={ this.state.provider } >
        <Radio value="aws">AWS</Radio>
        <Radio value="gcp">GCP</Radio>
        <Radio value="azure">Azure</Radio>
      </RadioGroup>
              <FormItemInput
                id="instance"
                label="Instance Name"
                value={ this.state.instance }
                onChange={ (event) => this.setState({ instance: event.target.value }) } />
                <FormItemInput
                id="location"
                label="Location"
                value={ this.state.location }
                onChange={ (event) => this.setState({ location: event.target.value }) } />
            </FormSection>
            
          </FormLayout>
            {/* <StackingLayout padding="20px">
             <FormItemInput id="1" label="Memory(GB)" placeholder={this.state.inputArray[0]} defaultValue={this.state.inputArray[0]} 
              suffix={ customSuffix } value={this.state.inputValue}/>
              <FormItemInput id="2" label="vCPUs" placeholder={this.state.inputArray[1]} defaultValue={this.state.inputArray[1]} />
              <FormItemInput id="3" label="Region" placeholder={this.state.inputArray[2]} defaultValue={this.state.inputArray[2]} />
              <FormItemInput id="4" label="Instance Storage(GB)" placeholder={this.state.inputArray[3]} defaultValue={this.state.inputArray[3]}
              suffix={ customSuffix }/>
              <FormItemInput id="5" label="Cloud Provider" placeholder={this.state.inputArray[4]}  defaultValue={this.state.inputArray[4]}  />
            </StackingLayout> */}
          </Modal>

        </div>
        {/* <SubmitModal /> */}
        </div>
      <StackingLayout padding ="20px">
      {this.displayTable()}
        {/* <Table rowKey="key" dataSource={this.state.data} columns={columns} pagination={pagination} sort={sort} sorters={sorters} rowSelection={rowSelection}/> */}
      </StackingLayout>
      </div>
    );

    return (
      <div>
      <MainPageLayout
        fullPage={true}
        leftPanel={leftPanel}
        leftPanelVisible={this.state.leftPanelVisible}
        header = {header}
        body= {body}
      />
      </div>);
  }
}
