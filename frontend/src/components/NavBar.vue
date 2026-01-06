<template>
  <nav class="uk-navbar-container">
    <div class="uk-container">
      <div uk-navbar>
        <div class="uk-navbar-left">
          <ul class="uk-navbar-nav">
            <li :class="{ 'uk-active': $route.path === '/' }">
              <router-link to="/">Главная</router-link>
            </li>
            <li>
              <a>Продукция</a>
              <div class="uk-navbar-dropdown">
                <ul class="uk-nav uk-navbar-dropdown-nav">
                  <li :class="{ 'uk-active': $route.path === '/products' }">
                    <router-link to="/products">Все товары</router-link>
                  </li>
                  <li><a href="#">Категория 1</a></li>
                  <li><a href="#">Категория 2</a></li>
                </ul>
              </div>
            </li>
            <li :class="{ 'uk-active': $route.path === '/about' }">
              <router-link to="/about">О нас</router-link>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </nav>
</template>

<script lang="ts">
export default {
  name: 'Navbar'
}
</script>