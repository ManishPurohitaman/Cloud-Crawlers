import React from 'react';
import { Progress ,TextLabel} from '@nutanix-ui/prism-reactjs';

const wrapper = {
    width: '260px'
  };

export default class Progbar extends React.Component {
    constructor(props){
        super(props);

    }
        render(){
        return (
        <Progress style={wrapper}
        percent={ this.props.num / this.props.total *100 }
        status="success"
        tooltipProps={ true }
        label={
          <TextLabel type={ TextLabel.TEXT_LABEL_TYPE.SECONDARY }>
            {this.props.num}/ {this.props.total}
          </TextLabel>
        }
      />
        );
    }
        
}