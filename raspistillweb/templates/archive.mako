# -*- coding: utf-8 -*- 
<%inherit file="archive-layout.mako"/>

<div class="container">
  <div class="row">
  % for file in database:     
    <div class="col-sm-6 col-md-4 col-lg-3">
      <div class="card my-3">
          <a href="${request.static_path('raspistillweb:pictures/', _scheme='https')}${file['filename']}">
            <img src="${request.static_path('raspistillweb:thumbnails/', _scheme='https')}${file['filename']}" alt="${file['filename']}" class="card-img-top">
          </a> 
        <div class="card-body">
          <dl>
            <dt>Date</dt>
            <dd>${file['date']}</dd>
            <dt>Resolution</dt>
            <dd>${file['resolution']}</dd>
            <dt>Filesize</dt>
            <dd>${file['filesize']}</dd>
          </dl>
          <form action="delete_picture" method="POST">
            <button type="submit" name="id" value="${file['id']}" class="btn btn-danger">Delete</button>
          </form>
        </div>
      </div>     
    </div>   
  % endfor 
  </div>
</div>