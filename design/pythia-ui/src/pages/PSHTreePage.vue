<i18n>
en:
    descendants: Subcategories
    work_count: Work count
    score: Interest
    avg_score: Average interest
    label:
        font_size: Font size reflects the number of works
        color: 'Color reflects interest (blue: small, red: big)'
        font_scaling: Font scaling


cs:
    descendants: Podkategorie
    work_count: Počet děl
    score: Zájem
    avg_score: Průměrný zájem
    label:
        font_size: Velikost fontu vyjadřuje počet děl
        color: 'Barva vyjadřuje zájem (modrá: malý, červená: velký)'
        font_scaling: Škálování fontu
</i18n>

<template>
  <v-container v-if="miUUID">
    <v-row>
      <v-col cols="auto" class="pr-4">
        <v-switch
          v-model="colorByInterest"
          :label="$t('label.color')"
          class="mt-0"
        ></v-switch>
      </v-col>
      <v-col cols="auto" class="pr-4">
        <v-switch
          v-model="fontSizeByTopicSize"
          :label="$t('label.font_size')"
          class="mt-0"
        ></v-switch>
      </v-col>
      <v-col>
        <v-slider
          class="mt-0"
          v-model="fontScalingRatio"
          thumb-label
          :disabled="!fontSizeByTopicSize"
          :label="$t('label.font_scaling')"
          :min="1"
          :max="66"
          track-color="secondary"
          style="min-width: 20rem"
        ></v-slider>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" :md="6">
        <v-treeview
          :items="items"
          :load-children="fetchChildren"
          :open.sync="open"
          :active.sync="active"
          activatable
          active-class="primary--text"
          class="grey lighten-5"
          loading-icon="fa-spinner"
          transition
        >
          <template v-slot:label="{ item }">
            <v-tooltip bottom>
              <template v-slot:activator="{ on }">
                <span v-on="on">
                  <span :style="itemStyle(item)">{{ item.name }}</span>
                  <span class="extra-data"
                    ><span class="size">{{ item.size }}</span> ({{
                      formatNumber(item.score)
                    }})</span
                  >
                </span>
              </template>
              <span>
                {{ $t("work_count") }}: {{ item.size }}<br />
                {{ $t("score") }}: {{ item.score }}
              </span>
            </v-tooltip>
          </template>
        </v-treeview>
      </v-col>
      <v-col cols="12" :md="6" v-if="activeItemId">
        <PSHConceptDetail
          :pshid="activeItemId"
          :miUUID="miUUID"
          :key="activeItemId"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from "axios";
import * as math from "mathjs";
import PSHConceptDetail from "../components/PSHConceptDetail";

export default {
  name: "PSHTreePage",
  components: { PSHConceptDetail },
  data() {
    return {
      tree: [],
      items: [],
      loading: false,
      open: [],
      active: [],
      numberFormat: {
        notation: "fixed",
        precision: 3,
      },
      activeItemData: null,
      activeItemLoading: false,
      colorByInterest: true,
      fontSizeByTopicSize: true,
      fontScalingRatio: 15,
    };
  },
  computed: {
    miUUID() {
      const mi = this.$store.getters.selectedModelInstance;
      if (mi) return mi.uuid;
      return null;
    },
    data_url() {
      if (this.miUUID) {
        return `/api/bookrank/mi/${this.miUUID}/psh-tree/`;
      } else return null;
    },
    activeItemId() {
      if (this.active.length) {
        return this.active[0];
      }
      return null;
    },
    activeItem() {
      return null;
    },
  },
  watch: {
    miUUID() {
      this.fetchData();
    },
  },
  methods: {
    fetchData() {
      if (this.miUUID) {
        this.loading = true;
        axios.get(this.data_url).then(
          (response) => {
            this.items = response.data;
            this.loading = false;
          },
          (error) => {
            this.$store.dispatch("showSnackbar", {
              content: "Error fetching data: " + error,
            });
            this.loading = false;
          }
        );
      }
    },
    fetchActiveItemData() {
      if (this.miUUID && this.activeItemId) {
        this.loading = true;
        axios.get(this.data_url).then(
          (response) => {
            this.items = response.data;
            this.loading = false;
          },
          (error) => {
            this.$store.dispatch("showSnackbar", {
              content: "Error fetching data: " + error,
            });
            this.loading = false;
          }
        );
      }
    },
    formatNumber(number) {
      return math.format(number, this.numberFormat);
    },
    itemStyle(item) {
      const rel_score = Math.sqrt(item.relative_score) * 2 - 1;
      let h = 300 + 60 * rel_score;
      const result = {};
      if (this.colorByInterest) {
        result["color"] = `hsl(${h}, 90%, 30%)`;
      }
      if (this.fontSizeByTopicSize) {
        result["fontSize"] =
          13 + this.fontScalingRatio * item.relative_size + "px";
      }
      return result;
    },
    async fetchChildren(parent) {
      const url = this.data_url + parent.id;
      return axios.get(url).then(
        (response) => {
          parent.children = response.data;
          // this.loading = false
        },
        (error) => {
          this.$store.dispatch("showSnackbar", {
            content: "Error fetching data: " + error,
          });
          this.loading = false;
        }
      );
    },
  },
  created() {
    this.fetchData();
  },
};
</script>

<style scoped lang="scss">
.extra-data {
  font-size: 12px;
  color: #888888;
  margin-left: 0.75rem;

  .size {
    font-weight: bold;
    font-style: italic;
    margin-right: 0.15rem;
  }
}
</style>
