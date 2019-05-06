# -*- coding: utf-8 -*- 
<%inherit file="settings-layout.mako"/>

<div class="container">
  % if preferences_success_alert:
    <div class="row">
      <div class="col-lg-10 col-lg-offset-1 mt-3 mx-auto">
        <div class="alert alert-success alert-dismissable fade show">
          <button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>
          <strong>Success!</strong> Settings saved. Please follow <a href="/photo" class="alert-link">this link</a> to take a photo.
        </div>
      </div>
    </div>
  % endif
  % if preferences_fail_alert != []: 
    <div class="row">
      <div class="col-lg-10 col-lg-offset-1 mt-3 mx-auto">
        <div class="alert alert-danger alert-dismissable fade show">
          <button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>
          <strong>Error!</strong> <br>
          <ul>
            % for alert in preferences_fail_alert:
              <li>${alert}</li>  
            % endfor
          </ul>
        </div>
      </div>
    </div>
  % endif
  <div class="row">
    <div class="col-lg-10 col-lg-offset-1 my-3 mx-auto">
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Settings</h3>
        </div>
        <div class="card-body">
      	  <form action="save" method="POST" role="form">
            <h4 class="form-text">Image preferences</h4>            
            <div class="form-group row">
              <label for="imageResolution1" class="col-xl-2 col-form-label">Resolution</label>
              <div class="col-md-3">
                <select name="imageResolution" class="form-control" id="imageResolution1">
                      <option selected>${image_width}x${image_height}</option>
                  % for resolution in image_resolutions:
                    % if resolution != image_width + 'x' + image_height:                               
                      <option>${resolution}</option>
                      % endif
                  % endfor
                </select>
              </div>

              <div class="col-md-1">
                <label for="imageResolution2" class="col-form-label">or</label>
              </div>
                            
              <div class="col-lg-4 col-xl-3 col-md-4">
                <div class="input-group" id="imageResolution2">
                  <div class="input-group-prepend">
                    <span class="input-group-text">width</span>
                  </div>
                  <input type="number" class="form-control" name="imageWidth" placeholder="${image_width}">
                </div>
              </div>
              <div class="col-lg-4 col-xl-3 col-md-4">
                <div class="input-group">
                  <div class="input-group-prepend">
                    <span class="input-group-text" id="">height</span>
                  </div>
                  <input type="number" class="form-control" name="imageHeight" placeholder="${image_height}">
                </div>                
              </div>
            </div>
            
            <div class="form-group row">
              <label for="ecodingMode1" class="col-lg-2 control-label">Encoding Mode</label>
              <div class="col-xl-10">
                <select name="encodingMode" class="form-control" id="encodingMode1">
                  % for mode in encoding_modes:
                    % if mode == encoding_mode:
                      <option selected>${mode}</option>
                    % else:
                      <option>${mode}</option>
                    % endif
                  % endfor
                </select>
              </div>
            </div>
            
            <div class="form-group row">
              <label for="isoOption1" class="col-lg-2 control-label">ISO Option</label>
              <div class="col-xl-10">
                <select name="isoOption" class="form-control" id="isoOption1">
                  % for option in iso_options:
                    % if option == image_iso:
                      <option selected>${option}</option>
                    % else:
                      <option>${option}</option>
                    % endif
                  % endfor
                </select>
              </div>
            </div>
            
            <div class="form-group row">
              <label for="exposureMode1" class="col-xl-2 col-form-label">Exposure Mode</label>
              <div class="col-xl-10">
                <select name="exposureMode" class="form-control" id="exposureMode1">
                  % for mode in exposure_modes:
                    % if mode == exposure_mode:
                      <option selected>${mode}</option>
                    % else:
                      <option>${mode}</option>
                    % endif
                  % endfor
                </select>
              </div>
            </div>
            <div class="form-group row">
              <label for="imageEffect1" class="col-xl-2 col-form-label">Image Effect</label>
              <div class="col-xl-10">
                <select name="imageEffect" class="form-control" id="imageEffect1">             
                  % for effect in image_effects:
                    % if effect == image_effect:
                      <option selected>${effect}</option>
                    % else:
                      <option>${effect}</option>
                    % endif
                  % endfor
                </select>
              </div>  
            </div>
            <div class="form-group row">
              <label for="awbMode1" class="col-xl-2 col-form-label">AWB Mode</label>
              <div class="col-xl-10">
                <select name="awbMode" class="form-control" id="awbMode1">             
                  % for mode in awb_modes:
                    % if mode == awb_mode:
                      <option selected>${mode}</option>
                    % else:
                      <option>${mode}</option>
                    % endif
                  % endfor
                </select>
              </div>  
            </div>
            <div class="form-group row">
              <label for="warmupDuration" class="col-xl-2 col-form-label">Warm-up</label>
              <div class="input-group col-xl-10">
                <input type="number" class="form-control" id="warmupDuration" name="warmupDuration" placeholder="${warmup_duration}">
                <div class="input-group-append">
                  <span class="input-group-text">s</span>
                </div>
              </div>
            </div>
            <div class="form-group row">
              <label for="imageRotation1" class="col-xl-2 col-form-label">Image Rotation</label>
              <div class="col-xl-10">
                <div class="btn-group" data-toggle="buttons">
                  <label class="btn btn-default ${'active' if image_rotation == '0' else ''}">
                    <input type="radio" name="imageRotation" value="0" ${'checked' if image_rotation == '0' else ''}><span class="glyphicon glyphicon-circle-arrow-up"></span> 0°
                   </label>
                  <label class="btn btn-default ${'active' if image_rotation == '90' else ''}">
                    <input type="radio" name="imageRotation" value="90" ${'checked' if image_rotation == '90' else ''}><span class="glyphicon glyphicon-circle-arrow-right"></span> 90°
                  </label>
                  <label class="btn btn-default ${'active' if image_rotation == '180' else ''}">
                    <input type="radio" name="imageRotation" value="180" ${'checked' if image_rotation == '180' else ''}><span class="glyphicon glyphicon-circle-arrow-down"></span> 180°
                  </label>
                  <label class="btn btn-default ${'active' if image_rotation == '270' else ''}">
                    <input type="radio" name="imageRotation" value="270" ${'checked' if image_rotation == '270' else ''}><span class="glyphicon glyphicon-circle-arrow-left"></span> 270°
                  </label>
                </div>
              </div>  
            </div>
            <h4 class="form-text">Time-lapse preferences</h4>
      	    <div class="form-group row">
              <label for="TimelapseInterval1" class="col-xl-2 col-form-label">Interval</label>
              <div class="input-group col-xl-10">
                <input type="number" class="form-control" id="TimelapseInterval1" name="timelapseInterval" placeholder="${timelapse_interval}">
                <div class="input-group-append">
                  <select name="timelapseIntervalUnit" class="form-control" id="timelapseIntervalUnit">             
                  % for unit in timelapse_units:
                    % if unit == timelapse_interval_unit:
                      <option selected>${unit}</option>
                    % else:
                      <option>${unit}</option>
                    % endif
                  % endfor
                </select>
                </div>
              </div>
            </div>
      	    <div class="form-group row">
              <label for="TimelapseTime1" class="col-xl-2 col-form-label">Duration</label>
              <div class="input-group col-xl-10">
                <input type="number" class="form-control" id="TimelapseTime1" name="timelapseTime" placeholder="${timelapse_time}">
                <div class="input-group-append">
                  <select name="timelapseTimeUnit" class="form-control" id="timelapseTimeUnit">             
                    % for unit in timelapse_units:
                      % if unit == timelapse_time_unit:
                        <option selected>${unit}</option>
                      % else:
                        <option>${unit}</option>
                      % endif
                    % endfor
                  </select>
                </div>
              </div>
            </div>
            <div class="form-group row">
              <div class="col-xl-2" col-form-label">Consistent Images</div>
              <div class="col-xl-10">
                <div class="form-check">
                  <input type="checkbox" class="form-check-input" value="1" id="timelapseConsistentMode" name="timelapseConsistentMode" aria-describedby="ConsistentModeHelpInline" ${'checked' if timelapse_consistent_mode == True else ''}>
                  <label for="timelapseConsistentMode" class="form-checklabel">Enable</label>
                  <small id="ConsistentModeHelpInline" class="form-text text-muted">Take all images with identical settings.</small>
                </div>
              </div>
            </div>
            <div class="form-group row">
              <div class="col-xl-offset-2 col-xl-10">
                <button type="submit" class="btn btn-primary">Save</button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div> 
</div>
