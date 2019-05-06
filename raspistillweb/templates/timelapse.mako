# -*- coding: utf-8 -*- 
<%inherit file="timelapse-layout.mako"/>

<div class="container">
  <div class="row">
    % if timelapse:
      <div class="col-lg-12 mt-3 mx-auto">
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
          <button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>
          <p class="card-text mb-3"><strong>Timelapse in Progress.</strong> Please wait until the timelapse process has finished or stop by pressing the button below.</p>
          <div class="progress mb-3">
            <div id="progressbar" class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" aria-valuenow="${percentage_completed}%" aria-valuemin="0" aria-valuemax="100" style="width: ${percentage_completed}%;">${percentage_completed}%</div>
          </div>
          <a class="btn btn-danger btn-lg" role="button" href="/stop_timelapse">Stop time-lapse</a>
        </div>
      </div>
    % else:
    <div class="col-lg-12">
      <div class="card my-3">
        <div class="card-header">
            <h3 class="card-title">Timelapse</h3>
          </div>
          <div class="card-body">
            <p class="card-text mb-3">
            There is currently no timelapse in progress. You can start a timelapse with the following settings. Other options can be changed on the <a href="/settings"><strong>settings page.</strong></a>
            </p>
            <form action="timelapse_start" method="POST" role="form">
              <div class="form-group row">
                <label for="timelapseInterval" class="col-form-label col-xl-2">Interval</label>
                <div class="input-group col-xl-10">
                  <input type="number" class="form-control" name="timelapseInterval" id="timelapseInterval" placeholder="${timelapseInterval}">
                  <div class="input-group-append">
                     <select name="timelapseIntervalUnit" class="form-control" id="timelapseIntervalUnit">             
                      % for unit in timelapseUnits:
                        % if unit == timelapseIntervalUnit:
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
                <label for="timelapseTime" class="col-form-label col-xl-2">Duration</label>
                <div class="input-group col-xl-10">
                  <input type="number" class="form-control" name="timelapseTime" id="timelapseTime" placeholder="${timelapseTime}">
                  <div class="input-group-append">
                    <select name="timelapseTimeUnit" class="form-control" id="timelapseTimeUnit">             
                      % for unit in timelapseUnits:
                        % if unit == timelapseTimeUnit:
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
              <label for="warmupDuration" class="col-xl-2 col-form-label">Warm-up</label>
              <div class="input-group col-xl-10">
                <input type="number" class="form-control" id="warmupDuration" name="warmupDuration" placeholder="${warmup_duration}">
                  <div class="input-group-append">
                    <span class="input-group-text">s</span>
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
              <input type="submit" class="btn btn-primary btn-lg" value="Start time-lapse">
            </form>
          </div>
      </div>
    </div>
    % endif    
  </div>
  <div class="row">
  % for file in timelapseDatabase:     
    <div class="col-sm-6 col-md-4 col-lg-3">
      <div class="card my-3">
        <div class="card-header">
          <h3 class="card-title">${file['timeStart']}</h3>
        </div>
        <div class="card-body">
          <dl>
            <dt>Number of Images</dt>
            <dd>${file['n_images']}</dd>
            <dt>Image Resolution</dt>
            <dd>${file['resolution']}</dd>
            <dt>Encoding Mode</dt>
            <dd>${file['encoding_mode']}</dd>
            <dt>Image Effect</dt>
            <dd>${file['image_effect']}</dd>
            <dt>Exposure Mode</dt>
            <dd>${file['exposure_mode']}</dd>
            <dt>AWB Mode</dt>
            <dd>${file['awb_mode']}</dd>
            <dt>Start</dt>
            <dd>${file['timeStart']}</dd>
            <dt>End</dt>
            <dd>${file['timeEnd']}</dd>
          </dl>
          <form action="delete_timelapse" method="POST">
            <button type="submit" name="id" value="${file['id']}" class="btn btn-danger btn-sm btn-block mb-2">Delete</button>
          </form>
          <a href="${request.static_url('raspistillweb:time-lapse/')}${file['filename']}.tar.gz" class="btn btn-success btn-sm btn-block">Download</a>
        </div>
      </div>     
    </div>   
  % endfor  
  </div>  
</div>
  	

