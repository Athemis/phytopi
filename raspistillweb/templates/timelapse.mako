# -*- coding: utf-8 -*- 
<%inherit file="timelapse-layout.mako"/>

<div class="container">
  <div class="row">
    % if timelapse:
      <div class="col-lg-12">
        <div class="alert alert-danger alert-dismissable fade show">
          <button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>
          <strong>Timelapse in Progress.</strong> Please wait until the timelapse process has finished.
          <div class="progress">
            <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" aria-valuenow="${percentage_completed}%" aria-valuemin="0" aria-valuemax="100" style="width: ${percentage_completed}%;">${percentage_completed}%</div>
          </div>        
        </div>
      </div>
    % else:
    <div class="col-lg-12">
      <div class="card my-3">
        <div class="card-header">
            <h3 class="card-title">Timelapse</h3>
          </div>
          <div class="card-body">
            There is currently no timelapse in progress. You can start a timelapse with the folowing preferences or edit these settings on the <a href="/settings"><strong>settings page.</strong></a>
            <form method="post">
              <div class="form-group row">
                <label for="timelapseInterval" class="col-form-label col-xl-2">Interval</label>
                <div class="input-group col-xl-10">
                  <input type="number" class="form-control" id="timelapseInterval" placeholder="${timelapseInterval}">
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
                  <input type="number" class="form-control" id="timelapseTime" placeholder="${timelapseTime}">
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
              <input type="button" class="btn btn-primary btn-lg" value="Start Timelapse" onclick="location.href='/timelapse_start'">
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
  	

