function post() {
  let comment = $('#textarea-post').val();
  let today = new Date().toISOString();
  $.ajax({
    type: 'POST',
    url: '/posting',
    data: {
      comment_give: comment,
      date_give: today,
    },
    success: function (response) {
      $('#modal-post').removeClass('is-active');
      window.location.reload();
    },
  });
}

function post_chatting(username) {
  if (username == undefined) {
    username = '';
  }

  let comment = $('#text-chat').val();
  console.log(username);
  let today = new Date().toISOString();
  $.ajax({
    type: 'POST',
    url: '/posting_chat',
    data: {
      comment_give: comment,
      date_give: today,
      username: username,
    },
    success: function (response) {
      $('#modal-post').removeClass('is-active');
      window.location.reload();
    },
  });
}

function time2str(date) {
  let today = new Date();
  let time = (today - date) / 1000 / 60; // minutes

  if (time < 60) {
    return parseInt(time) + ' minutes ago';
  }
  time = time / 60; // hours
  if (time < 24) {
    return parseInt(time) + ' hours ago';
  }
  time = time / 24; // days
  if (time < 7) {
    return parseInt(time) + ' days ago';
  }
  return `${date.getFullYear()}.${date.getMonth() + 1}.${date.getDate()}`;
}
function num2str(count) {
  if (count > 10000) {
    return parseInt(count / 1000) + 'k';
  }
  if (count > 500) {
    return parseInt(count / 100) / 10 + 'k';
  }
  if (count == 0) {
    return '';
  }
  return count;
}

function get_chats(username) {
  if (username == undefined) {
    username = '';
  }
  $('.chat').empty();
  $.ajax({
    type: 'GET',
    url: `/get_chat?username_give=${username}`,
    data: {},
    success: function (response) {
      if (response['result'] === 'success') {
        let posts = response['posts'];
        console.log(posts);
        for (let i = 0; i < posts.length; i++) {
          let post = posts[i];
          let time_post = new Date(post['date_dec']);
          let time_before = time2str(time_post);

          if (post['jenis'] == 'kawan') {
            var isTrue = true;
          } else {
            var isTrue = false;
          }
          let chat_html = `
          <div class="m-messenger__datetime">${time_before}</div>
        ${
          isTrue
            ? `<div class="m-messenger__wrapper">
                    <div class="m-messenger__message m-messenger__message--in">
                      <div class="m-messenger__message-pic">
                      <a class="image is-64x64" href="/user/${post['username']}">
                      <img class="is-rounded" src="/static/${post['profile_pic_real_dec']}"
                           alt="">
                        </a>
                      </div>
                      <div class="m-messenger__message-body">
                        <div class="m-messenger__message-arrow"></div>
                        <div class="m-messenger__message-content">
                          <div class="m-messenger__message-username"><strong>${post['profile_name_dec']}</strong> <small>@${post['username']}</small></div>
                          <div class="m-messenger__message-text">${post['isi_chat_dec']}</div>
                        </div>
                      </div>
                    </div>
                  </div>`
            : `<div class="m-messenger__wrapper">
                    <div class="m-messenger__message m-messenger__message--out">
                      <div class="m-messenger__message-body">
                        <div class="m-messenger__message-arrow"></div>
                        <div class="m-messenger__message-content">
                          <div class="m-messenger__message-text">${post['isi_chat_dec']}</div>
                        </div>
                      </div>
                    </div>
                  </div>`
        }`;

          $('.chat').append(chat_html);
        }
      }
    },
  });
}

function get_posts(username) {
  if (username == undefined) {
    username = '';
  }
  $('#post-box').empty();
  $.ajax({
    type: 'GET',
    url: `/get_posts?username_give=${username}`,
    data: {},
    success: function (response) {
      if (response['result'] === 'success') {
        let posts = response['posts'];

        for (let i = 0; i < posts.length; i++) {
          let post = posts[i];
          console.log(post['comment']['ciphertext']);
          let time_post = new Date(post['date']);
          let time_before = time2str(time_post);
          let class_heart = post['heart_by_me'] ? 'fa-heart' : 'fa-heart-o';
          let class_star = post['star_by_me'] ? 'fa-star' : 'fa-star-o';
          let class_like = post['like_by_me'] ? 'fa-thumbs-up' : 'fa-thumbs-o-up';

          let html_temp = `<div class="box" id="${post['_id']}">
                                          <article class="media">
                                              <div class="media-left">
                                                  <a class="image is-64x64" href="#">
                                                      <img class="is-rounded" src="/static/${post['profile_pic_real']}"
                                                           alt="Image">
                                                  </a>
                                              </div>
                                              <div class="media-content">
                                                  <div class="content">
                                                      <p>
                                                          <strong>${post['profile_name']}</strong> <small>@${post['username']}</small> <small>${time_before}</small>
                                                          <br>
                                                          ${post['isi_pesan']}
                                                      </p>
                                                  </div>
                                                  <nav class="level is-mobile">
                                                      <div class="level-left">
                                                          <a class="level-item is-sparta" aria-label="heart" onclick="toggle_like('${post['_id']}', 'heart')">
                                                              <span class="icon is-small"><i class="fa ${class_heart}"
                                                                                             aria-hidden="true"></i></span>&nbsp;<span class="like-num">${num2str(post['count_heart'])}</span>
                                                          </a>
                                                          <a class="level-item is-sparta" aria-label="star" onclick="toggle_star('${post['_id']}', 'star')">
                                                              <span class="icon is-small"><i class="fa ${class_star}"
                                                                                             aria-hidden="true"></i></span>&nbsp;<span class="like-num">${num2str(post['count_star'])}</span>
                                                          </a>
                                                          <a class="level-item is-sparta" aria-label="like" onclick="toggle_thumbsup('${post['_id']}', 'like')">
                                                              <span class="icon is-small"><i class="fa ${class_like}"
                                                                                             aria-hidden="true"></i></span>&nbsp;<span class="like-num">${num2str(post['count_like'])}</span>
                                                          </a>
                                                      </div>
  
                                                  </nav>
                                              </div>
                                          </article>
                                      </div>`;
          $('#post-box').append(html_temp);
          if (post['jenis'] == 'kawan') {
            var isTrue = true;
          } else {
            var isTrue = false;
          }
          let chat_html = `
          <div class="m-messenger__datetime">2:30PM</div>
        ${
          isTrue
            ? `<div class="m-messenger__wrapper">
                    <div class="m-messenger__message m-messenger__message--in">
                      <div class="m-messenger__message-pic">
                        <img src="../../static/assets/app/media/img//users/user3.jpg" alt="" />
                      </div>
                      <div class="m-messenger__message-body">
                        <div class="m-messenger__message-arrow"></div>
                        <div class="m-messenger__message-content">
                          <div class="m-messenger__message-username">Megan wrote</div>
                          <div class="m-messenger__message-text">Will the development team be joining ?</div>
                        </div>
                      </div>
                    </div>
                  </div>`
            : `<div class="m-messenger__wrapper">
                    <div class="m-messenger__message m-messenger__message--out">
                      <div class="m-messenger__message-body">
                        <div class="m-messenger__message-arrow"></div>
                        <div class="m-messenger__message-content">
                          <div class="m-messenger__message-text">Yes sure. I invited them as well</div>
                        </div>
                      </div>
                    </div>
                  </div>`
        }`;

          $('.chat').append(chat_html);
        }
      }
    },
  });
}

function get_user(username) {
  if (username == undefined) {
    username = '';
  }
  $('.data_user').empty();
  $.ajax({
    type: 'GET',
    url: `/data_user`,
    data: {},
    success: function (response) {
      if (response['result'] === 'success') {
        let posts = response['posts'];
        for (let i = 0; i < posts.length; i++) {
          let post = posts[i];
          let html_temp = `<li class="m-menu__item m-menu__item--active" aria-haspopup="true">
            <a href="/chatting/${post['username']}" class="m-menu__link">
            <i class="m-menu__link-bullet m-menu__link-bullet--dot">
              <span></span>
            </i>
            <span class="m-menu__link-text">${post['username']}</span>
          </a>
        </li>`;
          $('.data_user').append(html_temp);
        }
      }
    },
  });
}

function toggle_like(post_id, type) {
  console.log(post_id, type);
  let $a_like = $(`#${post_id} a[aria-label='heart']`);
  let $i_like = $a_like.find('i');
  if ($i_like.hasClass('fa-heart')) {
    $.ajax({
      type: 'POST',
      url: '/update_like',
      data: {
        post_id_give: post_id,
        type_give: type,
        action_give: 'unlike',
      },
      success: function (response) {
        console.log('unlike');
        $i_like.addClass('fa-heart-o').removeClass('fa-heart');
        $a_like.find('span.like-num').text(num2str(response['count']));
      },
    });
  } else {
    $.ajax({
      type: 'POST',
      url: '/update_like',
      data: {
        post_id_give: post_id,
        type_give: type,
        action_give: 'like',
      },
      success: function (response) {
        console.log('like');
        $i_like.addClass('fa-heart').removeClass('fa-heart-o');
        $a_like.find('span.like-num').text(num2str(response['count']));
      },
    });
  }
}

function toggle_star(post_id, type) {
  console.log(post_id, type);
  let $a_like = $(`#${post_id} a[aria-label='star']`);
  let $i_like = $a_like.find('i');
  if ($i_like.hasClass('fa-star')) {
    $.ajax({
      type: 'POST',
      url: '/update_like',
      data: {
        post_id_give: post_id,
        type_give: type,
        action_give: 'unlike',
      },
      success: function (response) {
        console.log('unlike');
        $i_like.addClass('fa-star-o').removeClass('fa-star');
        $a_like.find('span.like-num').text(num2str(response['count']));
      },
    });
  } else {
    $.ajax({
      type: 'POST',
      url: '/update_like',
      data: {
        post_id_give: post_id,
        type_give: type,
        action_give: 'like',
      },
      success: function (response) {
        console.log('like');
        $i_like.addClass('fa-star').removeClass('fa-star-o');
        $a_like.find('span.like-num').text(num2str(response['count']));
      },
    });
  }
}

function toggle_thumbsup(post_id, type) {
  console.log(post_id, type);
  let $a_like = $(`#${post_id} a[aria-label='like']`);
  let $i_like = $a_like.find('i');
  if ($i_like.hasClass('fa-thumbs-up')) {
    $.ajax({
      type: 'POST',
      url: '/update_like',
      data: {
        post_id_give: post_id,
        type_give: type,
        action_give: 'unlike',
      },
      success: function (response) {
        console.log('unlike');
        $i_like.addClass('fa-thumbs-o-up').removeClass('fa-thumbs-up');
        $a_like.find('span.like-num').text(num2str(response['count']));
      },
    });
  } else {
    $.ajax({
      type: 'POST',
      url: '/update_like',
      data: {
        post_id_give: post_id,
        type_give: type,
        action_give: 'like',
      },
      success: function (response) {
        $i_like.addClass('fa-thumbs-up').removeClass('fa-thumbs-o-up');
        $a_like.find('span.like-num').text(num2str(response['count']));
      },
    });
  }
}

function sign_out() {
  $.removeCookie('mytoken', { path: '/' });
  alert('Signed out!');
  window.location.href = '/login';
}

function sign_out1() {
  document.cookie = 'mytoken=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
  alert('Signed out!');
  window.location.href = '/login';
}

function update_profile() {
  let name = $('#input-name').val();
  let file = $('#input-pic')[0].files[0];
  let about = $('#textarea-about').val();
  let form_data = new FormData();
  form_data.append('file_give', file);
  form_data.append('name_give', name);
  form_data.append('about_give', about);
  console.log(name, file, about, form_data);

  $.ajax({
    type: 'POST',
    url: '/update_profile',
    data: form_data,
    cache: false,
    contentType: false,
    processData: false,
    success: function (response) {
      if (response['result'] === 'success') {
        alert(response['msg']);
        window.location.reload();
      }
    },
  });
}
