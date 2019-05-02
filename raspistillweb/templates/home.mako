# -*- coding: utf-8 -*- 
<%inherit file="home-layout.mako"/>

<div class="container">
  % if timelapse:
    <div class="row">
      <div class="col-lg-12">
        <div class="alert alert-danger alert-dismissible fade show">
          <button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>
          <strong>Timelapse in progress.</strong> Currently it is not possible to take a photo. You can stop the timelapse if you follow <a href="/timelapse" class="alert-link">this link</a>.
        </div>
      </div>
    </div>
  % endif
  <div class="row">
    <div class="card my-3 mx-auto">
      <div class="row no-gutters">
        <div class="col-lg-8">
          <a href="${request.static_path('raspistillweb:pictures/'), _scheme='https'}${imagedata['filename']}">
            <img src="${request.static_path('raspistillweb:pictures/'), _scheme='https'}${imagedata['filename']}" class="card-img">
          </a>
        </div>
        <div class="col-lg-4">
          <div class="card-body">
            <h3 class="card-title">Image metadata</h3>
            <dl>
              <dt>Date</dt>
              <dd>${imagedata['date']}</dd>
              <dt>Filesize</dt>
              <dd>${imagedata['filesize']}</dd>
              <dt>Image Resolution</dt>
              <dd>${imagedata['resolution']}</dd>
              <dt>ISO</dt>
              <dd>${imagedata['ISO']}</dd>
              <dt>Exposure Time</dt>
              <dd>${imagedata['exposure_time']}</dd>
              <dt>Image Exposure Mode</dt>
              <dd>${imagedata['exposure_mode']}</dd>
              <dt>Image Effect</dt>
              <dd>${imagedata['image_effect']}</dd>
              <dt>AWB Mode</dt>
              <dd>${imagedata['awb_mode']}</dd>
            </dl>
          </div>
        </div>
      </div>
    </div>
  </div>  
</div>